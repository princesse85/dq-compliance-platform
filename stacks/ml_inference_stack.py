from typing import Dict, Any
from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_ecr as ecr,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_logs as logs,
    RemovalPolicy,
    Tags,
)

class MLInferenceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, 
                 project_prefix: str, env_name: str, analytics_bucket: s3.IBucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ---------- ECR Repository for Lambda Container ----------
        self.ecr_repo = ecr.Repository(
            self, "LegalInferRepo",
            repository_name=f"{project_prefix}-{env_name}-legal-infer-repo",
            image_scan_on_push=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
        )

        # ---------- Lambda Function (Container) ----------
        # IAM Role for Lambda
        lambda_role = iam.Role(
            self, "LegalInferLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
            ],
        )

        # S3 read access to analytics bucket
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:ListBucket"],
                resources=[
                    analytics_bucket.bucket_arn,
                    analytics_bucket.arn_for_objects("*"),
                ],
            )
        )

        # CloudWatch Logs
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                resources=["*"],
            )
        )

        # Create Lambda function
        self.lambda_function = lambda_.DockerImageFunction(
            self, "LegalInferFunction",
            function_name=f"{project_prefix}-{env_name}-legal-infer",
            code=lambda_.DockerImageCode.from_ecr(
                repository=self.ecr_repo,
                tag="latest",
            ),
            role=lambda_role,
            memory_size=2048,
            timeout=Duration.seconds(30),
            reserved_concurrent_executions=2,  # Budget guardrail
            environment={
                "ANALYTICS_BUCKET": analytics_bucket.bucket_name,
                "EXPLAIN_PREFIX": "explain",
                "MODEL_VARIANT": "baseline",  # Default, will be overridden by versions
                "LOG_LEVEL": "INFO",
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # ---------- API Gateway ----------
        api = apigateway.RestApi(
            self, "LegalInferAPI",
            rest_api_name=f"{project_prefix}-{env_name}-legal-infer-api",
            description="Legal compliance inference API with A/B testing",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"],
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True,
            ),
        )

        # Create /predict endpoint
        predict_integration = apigateway.LambdaIntegration(
            self.lambda_function,
            request_templates={
                "application/json": '{ "body": $input.json("$") }'
            },
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_templates={
                        "application/json": "$input.json('$')"
                    },
                ),
                apigateway.IntegrationResponse(
                    status_code="400",
                    selection_pattern=".*[ERROR].*",
                    response_templates={
                        "application/json": '{ "error": "Bad Request", "message": "$input.json(\'$.errorMessage\')" }'
                    },
                ),
            ],
        )

        predict_resource = api.root.add_resource("predict")
        predict_resource.add_method(
            "POST",
            predict_integration,
            request_models={
                "application/json": apigateway.Model.EMPTY_MODEL,
            },
            method_responses=[
                apigateway.MethodResponse(status_code="200"),
                apigateway.MethodResponse(status_code="400"),
                apigateway.MethodResponse(status_code="500"),
            ],
        )

        # ---------- SSM Parameters ----------
        ssm.StringParameter(
            self, "AnalyticsBucketParam",
            parameter_name=f"/{project_prefix}/{env_name}/analytics-bucket",
            string_value=analytics_bucket.bucket_name,
            description="Analytics bucket name for inference API",
        )

        ssm.StringParameter(
            self, "ExplainPrefixParam",
            parameter_name=f"/{project_prefix}/{env_name}/explain-prefix",
            string_value="explain",
            description="S3 prefix for explanation HTML files",
        )

        ssm.StringParameter(
            self, "ApiEndpointParam",
            parameter_name=f"/{project_prefix}/{env_name}/api-endpoint",
            string_value=api.url,
            description="API Gateway endpoint URL",
        )

        # ---------- Outputs ----------
        self.api_url = api.url
        self.ecr_repo_uri = self.ecr_repo.repository_uri
        self.lambda_function_name = self.lambda_function.function_name

        # ---------- Tags ----------
        Tags.of(self).add("Project", "LegalCompliance")
        Tags.of(self).add("Env", env_name)
        Tags.of(self).add("Phase", "4")

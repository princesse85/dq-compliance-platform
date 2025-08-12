from typing import Dict, Any, Optional
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
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_sns as sns,
    RemovalPolicy,
    Tags,
    CfnOutput,
)

class MLInferenceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, 
                 project_prefix: str, env_name: str, analytics_bucket: s3.IBucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ---------- ECR Repository for Lambda Container ----------
        self.ecr_repo = ecr.Repository(
            self, "MLInferenceECRRepo",
            repository_name=f"{project_prefix}-{env_name}-ml-inference-repo",
            image_scan_on_push=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
        )

        # ---------- SNS Topic for Alerts ----------
        self.alerts_topic = sns.Topic(
            self, "MLInferenceAlertsTopic",
            topic_name=f"{project_prefix}-{env_name}-ml-inference-alerts",
            display_name=f"{project_prefix}-{env_name}-ML-Inference-Alerts",
        )

        # ---------- IAM Role for Lambda ----------
        lambda_role = iam.Role(
            self, "MLInferenceLambdaRole",
            role_name=f"{project_prefix}-{env_name}-ml-inference-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
            ],
            inline_policies={
                "S3AccessPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:GetObjectVersion",
                                "s3:ListBucket",
                            ],
                            resources=[
                                analytics_bucket.bucket_arn,
                                analytics_bucket.arn_for_objects("*"),
                            ],
                        ),
                    ],
                ),
            },
        )

        # ---------- Lambda Function (Container) ----------
        self.lambda_function = lambda_.DockerImageFunction(
            self, "MLInferenceFunction",
            function_name=f"{project_prefix}-{env_name}-ml-inference",
            code=lambda_.DockerImageCode.from_ecr(
                repository=self.ecr_repo,
                tag="latest",
            ),
            role=lambda_role,
            memory_size=2048,
            timeout=Duration.seconds(30),
            reserved_concurrent_executions=5,
            environment={
                "ENVIRONMENT": env_name,
                "PROJECT_PREFIX": project_prefix,
                "ANALYTICS_BUCKET": analytics_bucket.bucket_name,
                "EXPLAIN_PREFIX": "explanations",
                "MODEL_VARIANT": "baseline",
                "LOG_LEVEL": "INFO",
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # ---------- API Gateway ----------
        api = apigateway.RestApi(
            self, "MLInferenceAPI",
            rest_api_name=f"{project_prefix}-{env_name}-ml-inference-api",
            description="ML inference API with A/B testing",
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
        )

        predict_resource = api.root.add_resource("predict")
        predict_resource.add_method(
            "POST",
            predict_integration,
            method_responses=[
                apigateway.MethodResponse(status_code="200"),
                apigateway.MethodResponse(status_code="400"),
                apigateway.MethodResponse(status_code="500"),
            ],
        )

        # Add health check endpoint
        health_resource = api.root.add_resource("health")
        health_integration = apigateway.LambdaIntegration(
            self.lambda_function,
            request_templates={
                "application/json": '{ "path": "/health" }'
            },
        )
        health_resource.add_method("GET", health_integration)

        # Add models status endpoint
        models_resource = api.root.add_resource("models")
        models_integration = apigateway.LambdaIntegration(
            self.lambda_function,
            request_templates={
                "application/json": '{ "path": "/models" }'
            },
        )
        models_resource.add_method("GET", models_integration)

        # ---------- Basic CloudWatch Alarms ----------
        # Lambda error rate alarm
        error_rate_alarm = cloudwatch.Alarm(
            self, "MLInferenceErrorRateAlarm",
            alarm_name=f"{project_prefix}-{env_name}-ml-inference-error-rate",
            metric=self.lambda_function.metric_errors(
                period=Duration.minutes(5),
                statistic="Sum",
            ),
            threshold=5,
            evaluation_periods=2,
        )
        error_rate_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alerts_topic))

        # Lambda duration alarm
        duration_alarm = cloudwatch.Alarm(
            self, "MLInferenceDurationAlarm",
            alarm_name=f"{project_prefix}-{env_name}-ml-inference-duration",
            metric=self.lambda_function.metric_duration(
                period=Duration.minutes(5),
                statistic="Average",
            ),
            threshold=25000,  # 25 seconds
            evaluation_periods=2,
        )
        duration_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alerts_topic))

        # ---------- SSM Parameters ----------
        ssm.StringParameter(
            self, "AnalyticsBucketParam",
            parameter_name=f"/{project_prefix}/{env_name}/ml-inference/analytics-bucket",
            string_value=analytics_bucket.bucket_name,
            description="Analytics bucket name for ML inference API",
        )

        ssm.StringParameter(
            self, "ApiEndpointParam",
            parameter_name=f"/{project_prefix}/{env_name}/ml-inference/api-endpoint",
            string_value=api.url,
            description="ML Inference API Gateway endpoint URL",
        )

        ssm.StringParameter(
            self, "ECRRepoUriParam",
            parameter_name=f"/{project_prefix}/{env_name}/ml-inference/ecr-repo-uri",
            string_value=self.ecr_repo.repository_uri,
            description="ECR repository URI for ML inference container",
        )

        # ---------- Outputs ----------
        CfnOutput(
            self, "ApiEndpointOutput",
            value=api.url,
            description="ML Inference API Gateway endpoint URL",
            export_name=f"{project_prefix}-{env_name}-ml-inference-api-url",
        )

        CfnOutput(
            self, "ECRRepoUriOutput",
            value=self.ecr_repo.repository_uri,
            description="ECR repository URI for ML inference container",
            export_name=f"{project_prefix}-{env_name}-ml-inference-ecr-uri",
        )

        CfnOutput(
            self, "LambdaFunctionNameOutput",
            value=self.lambda_function.function_name,
            description="ML Inference Lambda function name",
            export_name=f"{project_prefix}-{env_name}-ml-inference-lambda-name",
        )

        # ---------- Tags ----------
        Tags.of(self).add("Project", "EnterpriseDataQuality")
        Tags.of(self).add("Environment", env_name)
        Tags.of(self).add("Component", "MLInference")

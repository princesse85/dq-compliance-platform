
from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    aws_iam as iam,
    aws_cloudtrail as cloudtrail,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_glue as glue,
    aws_budgets as budgets,
    Tags,
    CfnOutput,
    aws_s3_notifications as s3n,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_ecr as ecr,
    aws_apigateway as apigateway,
    aws_ssm as ssm,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
)
from constructs import Construct

class MainStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, project_prefix: str, env_name: str, billing_email: str, monthly_budget: float, ecr_repo: ecr.IRepository, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Validate input parameters
        if monthly_budget <= 0:
            raise ValueError("monthly_budget must be a positive value")

        # ---------- S3 Buckets (dev-friendly: destroy on stack delete) ----------
        suffix = f"{self.account}-{self.region}".lower()

        self.raw_bucket = s3.Bucket(
            self, "RawBucket",
            bucket_name=f"{project_prefix}-raw-{env_name}-{suffix}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.processed_bucket = s3.Bucket(
            self, "ProcessedBucket",
            bucket_name=f"{project_prefix}-processed-{env_name}-{suffix}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.analytics_bucket = s3.Bucket(
            self, "AnalyticsBucket",
            bucket_name=f"{project_prefix}-analytics-{env_name}-{suffix}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.audit_bucket = s3.Bucket(
            self, "AuditLogsBucket",
            bucket_name=f"{project_prefix}-audit-{env_name}-{suffix}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # ---------- CloudTrail (multi-region) ----------
        trail = cloudtrail.Trail(
            self,
            "OrgTrail",
            bucket=self.audit_bucket,
            is_multi_region_trail=True,
            include_global_service_events=True,
            management_events=cloudtrail.ReadWriteType.ALL,
            enable_file_validation=True,
        )

        # ---------- SNS Alerts Topic ----------
        alerts_topic = sns.Topic(self, "AlertsTopic", topic_name=f"{project_prefix}-{env_name}-alerts")
        alerts_topic.add_subscription(subs.EmailSubscription(billing_email))

        # ---------- AWS Budget (monthly, email at 80% actual spend) ----------
        budgets.CfnBudget(
            self,
            "MonthlyCostBudget",
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_type="COST",
                time_unit="MONTHLY",
                budget_limit=budgets.CfnBudget.SpendProperty(amount=monthly_budget, unit="USD"),
                budget_name=f"{project_prefix}-{env_name}-monthly-budget",
            ),
            notifications_with_subscribers=[
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        notification_type="ACTUAL",
                        threshold_type="PERCENTAGE",
                        threshold=80,
                        comparison_operator="GREATER_THAN",
                    ),
                    subscribers=[
                        budgets.CfnBudget.SubscriberProperty(
                            subscription_type="EMAIL",
                            address=billing_email,
                        )
                    ],
                )
            ],
        )

        # ---------- Glue Data Catalog: database ----------
        glue.CfnDatabase(
            self,
            "GlueDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name=f"{project_prefix}_compliance_platform_{env_name}",
                description=f"Data catalog for {project_prefix} compliance platform ({env_name})",
            ),
        )

        # ---------- IAM Groups & Policies (least-privilege for Phase 0) ----------
        admins = iam.Group(self, "PlatformAdminsGroup", group_name=f"{project_prefix}-{env_name}-platform-admins")
        admins.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))

        # Data Engineers: scoped S3 + Glue access (dev-friendly)
        de_policy = iam.ManagedPolicy(
            self,
            "DataEngineersPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=["s3:ListBucket"],
                    resources=[self.raw_bucket.bucket_arn, self.processed_bucket.bucket_arn, self.analytics_bucket.bucket_arn],
                ),
                iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                    resources=[
                        self.raw_bucket.arn_for_objects("*"),
                        self.processed_bucket.arn_for_objects("*"),
                        self.analytics_bucket.arn_for_objects("*"),
                    ],
                ),
                iam.PolicyStatement(actions=["glue:*"], resources=["*"]),  # narrow later as needed
            ],
            description="Data engineers can work with project buckets and the Glue catalog.",
        )
        data_engineers = iam.Group(self, "DataEngineersGroup", group_name=f"{project_prefix}-{env_name}-data-engineers")
        data_engineers.add_managed_policy(de_policy)

        # Reviewers: read-only to analytics bucket
        reviewers_policy = iam.ManagedPolicy(
            self,
            "ReviewersPolicy",
            statements=[
                iam.PolicyStatement(actions=["s3:ListBucket"], resources=[self.analytics_bucket.bucket_arn]),
                iam.PolicyStatement(actions=["s3:GetObject"], resources=[self.analytics_bucket.arn_for_objects("*")]),
            ],
            description="Reviewers can read analytics outputs only.",
        )
        reviewers = iam.Group(self, "ReviewersGroup", group_name=f"{project_prefix}-{env_name}-reviewers")
        reviewers.add_managed_policy(reviewers_policy)

        # ---------- S3 Event Notification Topic for Raw Bucket ----------
        self.raw_bucket_events_topic = sns.Topic(
            self, "RawBucketEventsTopic",
            topic_name=f"{project_prefix}-{env_name}-raw-bucket-events"
        )

        # Add S3 event notification to raw_bucket to publish to the new SNS topic
        self.raw_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.SnsDestination(self.raw_bucket_events_topic),
            s3.NotificationKeyFilter(prefix="docs/") # Only for objects in 'docs/' prefix
        )

        # Export the ARN of the raw bucket events topic
        CfnOutput(
            self, "RawBucketEventsTopicArn",
            value=self.raw_bucket_events_topic.topic_arn,
            description="ARN of the SNS topic for raw bucket object creation events",
            export_name=f"{project_prefix}-{env_name}-RawBucketEventsTopicArn",
        )

        # ---------- Tags ----------
        for b in [self.raw_bucket, self.processed_bucket, self.analytics_bucket, self.audit_bucket]:
            Tags.of(b).add("Project", "LegalCompliance")
            Tags.of(b).add("Env", env_name)

        # ---- IAM role for Glue (crawlers + job) ----
        glue_role = iam.Role(
            self, "GlueServiceRole",
            role_name=f"{project_prefix}-{env_name}-glue-role",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
            ],
        )
        # Allow Glue to access project buckets
        glue_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:ListBucket"],
            resources=[
                self.raw_bucket.bucket_arn,
                self.processed_bucket.bucket_arn,
                self.analytics_bucket.bucket_arn,
            ],
        ))
        glue_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetObject","s3:PutObject","s3:DeleteObject"],
            resources=[
                f"{self.raw_bucket.bucket_arn}/*",
                f"{self.processed_bucket.bucket_arn}/*",
                f"{self.analytics_bucket.bucket_arn}/*",
            ],
        ))
        # Logs & metrics
        glue_role.add_to_policy(iam.PolicyStatement(
            actions=["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
            resources=["*"],
        ))

        # ---- Glue Database (already created in Phase 0) ----
        db_name = "legal_platform"

        # ---- Crawlers: Raw & Processed (Contract Register) ----
        raw_prefix = "contract_register/"  # under raw/
        processed_prefix = "contract_register/"  # under processed/

        glue.CfnCrawler(
            self, "RawContractsCrawler",
            name=f"{project_prefix}-{env_name}-raw-contracts",
            role=glue_role.role_arn,
            database_name=db_name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[glue.CfnCrawler.S3TargetProperty(
                    path=f"s3://{self.raw_bucket.bucket_name}/{raw_prefix}"
                )]
            ),
            schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                delete_behavior="LOG", update_behavior="UPDATE_IN_DATABASE"
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(recrawl_behavior="CRAWL_EVERYTHING"),
        )

        glue.CfnCrawler(
            self, "ProcessedContractsCrawler",
            name=f"{project_prefix}-{env_name}-processed-contracts",
            role=glue_role.role_arn,
            database_name=db_name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[glue.CfnCrawler.S3TargetProperty(
                    path=f"s3://{self.processed_bucket.bucket_name}/{processed_prefix}"
                )]
            ),
            schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                delete_behavior="LOG", update_behavior="UPDATE_IN_DATABASE"
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(recrawl_behavior="CRAWL_EVERYTHING"),
        )

        # ---- Glue ETL Job asset (PySpark script) ----
        # Use a more reliable path for the ETL script
        from aws_cdk import aws_s3_assets as assets
        etl_asset = assets.Asset(self, "ContractsEtlScript",
            path="src/etl_pipelines/contracts_etl_job.py"
        )

        glue.CfnJob(
            self, "ContractsEtlJob",
            name=f"{project_prefix}-{env_name}-contracts-etl",
            role=glue_role.role_arn,
            glue_version="4.0",  # Spark 3.3 / Py 3.10
            number_of_workers=2,
            worker_type="G.1X",
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                python_version="3",
                script_location=etl_asset.s3_object_url,
            ),
            default_arguments={
                "--job-language": "python",
                "--enable-metrics": "true",
                "--raw_bucket": self.raw_bucket.bucket_name,
                "--processed_bucket": self.processed_bucket.bucket_name,
                "--raw_prefix": raw_prefix,
                "--processed_prefix": processed_prefix,
                "--TempDir": f"s3://{self.analytics_bucket.bucket_name}/glue-tmp/",
                "--additional-python-modules": "boto3>=1.34.0"
            },
            execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=1),
            description="ETL: Clean contract register CSV -> Parquet with basic remediation",
            timeout=60,  # 60 minutes timeout
        )

        # Create SNS topic for Textract completion notifications
        textract_topic = sns.Topic(
            self, "TextractCompletionTopic",
            topic_name=f"{project_prefix}-{env_name}-textract-complete"
        )

        # Create IAM role for Textract to publish to SNS
        textract_publish_role = iam.Role(
            self, "TextractPublishRole",
            role_name=f"{project_prefix}-{env_name}-textract-publish-role",
            assumed_by=iam.ServicePrincipal("textract.amazonaws.com"),
        )
        textract_publish_role.add_to_policy(
            iam.PolicyStatement(
                actions=["sns:Publish"],
                resources=[textract_topic.topic_arn]
            )
        )

        # Create SQS queue with dead letter queue for reliable processing
        dead_letter_queue = sqs.Queue(
            self, "TextractDeadLetterQueue",
            queue_name=f"{project_prefix}-{env_name}-textract-dlq",
            retention_period=Duration.days(14)
        )
        
        textract_queue = sqs.Queue(
            self, "TextractProcessingQueue",
            queue_name=f"{project_prefix}-{env_name}-textract-queue",
            visibility_timeout=Duration.minutes(5),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3, 
                queue=dead_letter_queue
            )
        )
        
        # Subscribe SQS queue to SNS topic
        textract_topic.add_subscription(subs.SqsSubscription(textract_queue))

        # Define common IAM policies
        s3_access_policy = iam.PolicyStatement(
            actions=[
                "s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"
            ],
            resources=[
                self.raw_bucket.bucket_arn,
                f"{self.raw_bucket.bucket_arn}/*",
                self.processed_bucket.bucket_arn,
                f"{self.processed_bucket.bucket_arn}/*",
                self.analytics_bucket.bucket_arn,
                f"{self.analytics_bucket.bucket_arn}/*",
            ]
        )

        textract_access_policy = iam.PolicyStatement(
            actions=[
                "textract:StartDocumentTextDetection",
                "textract:StartDocumentAnalysis",
                "textract:GetDocumentTextDetection",
                "textract:GetDocumentAnalysis",
            ],
            resources=["*"]
        )

        # Create document processing router Lambda
        document_router = _lambda.Function(
            self, "DocumentRouterFunction",
            function_name=f"{project_prefix}-{env_name}-document-router",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_ingest_router.handler",
            code=_lambda.Code.from_asset("src/ocr"),
            timeout=Duration.minutes(2),
            memory_size=512,
            environment={
                "RAW_BUCKET": self.raw_bucket.bucket_name,
                "PROCESSED_BUCKET": self.processed_bucket.bucket_name,
                "ANALYTICS_BUCKET": self.analytics_bucket.bucket_name,
                "SNS_TOPIC_ARN": textract_topic.topic_arn,
                "TEXTRACT_PUBLISH_ROLE_ARN": textract_publish_role.role_arn,
                "LOW_CONF_THRESHOLD": "0.85",
            }
        )
        
        # Attach policies to document router
        document_router.add_to_role_policy(s3_access_policy)
        document_router.add_to_role_policy(textract_access_policy)
        document_router.add_to_role_policy(
            iam.PolicyStatement(
                actions=["sns:Publish", "iam:PassRole"], 
                resources=[textract_topic.topic_arn, textract_publish_role.role_arn]
            )
        )

        # Subscribe document router Lambda to the raw bucket events topic
        self.raw_bucket_events_topic.add_subscription(subs.LambdaSubscription(document_router))

        # Create Textract result processor Lambda
        textract_processor = _lambda.Function(
            self, "TextractProcessorFunction",
            function_name=f"{project_prefix}-{env_name}-textract-processor",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_textract_consumer.handler",
            code=_lambda.Code.from_asset("src/ocr"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            environment={
                "RAW_BUCKET": self.raw_bucket.bucket_name,
                "PROCESSED_BUCKET": self.processed_bucket.bucket_name,
                "ANALYTICS_BUCKET": self.analytics_bucket.bucket_name,
                "LOW_CONF_THRESHOLD": "0.85",
            }
        )
        
        # Attach policies to textract processor
        textract_processor.add_to_role_policy(s3_access_policy)
        textract_processor.add_to_role_policy(textract_access_policy)
        textract_queue.grant_consume_messages(textract_processor)

        # Create Glue crawlers for data cataloging
        database_name = "legal_platform"
        
        # Crawler for processed text files
        text_crawler = glue.CfnCrawler(
            self, "ProcessedTextCrawler",
            name=f"{project_prefix}-{env_name}-processed-text",
            role=iam.Role.from_role_name(
                self, "GlueRoleRef", 
                role_name=f"{project_prefix}-{env_name}-glue-role"
            ).role_arn,
            database_name=database_name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[glue.CfnCrawler.S3TargetProperty(
                    path=f"s3://{self.processed_bucket.bucket_name}/docs/text/"
                )]
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(
                recrawl_behavior="CRAWL_EVERYTHING"
            ),
        )

        # Crawler for processing metrics
        metrics_crawler = glue.CfnCrawler(
            self, "ProcessedMetricsCrawler",
            name=f"{project_prefix}-{env_name}-processed-metrics",
            role=iam.Role.from_role_name(
                self, "GlueRoleRefMetrics", 
                role_name=f"{project_prefix}-{env_name}-glue-role"
            ).role_arn,
            database_name=database_name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[glue.CfnCrawler.S3TargetProperty(
                    path=f"s3://{self.processed_bucket.bucket_name}/docs/metrics/"
                )]
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(
                recrawl_behavior="CRAWL_EVERYTHING"
            ),
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
                                self.analytics_bucket.bucket_arn,
                                self.analytics_bucket.arn_for_objects("*"),
                            ],
                        ),
                    ],
                ),
            },
        )

        # ---------- Lambda Function (Container) ----------
        self.lambda_function = _lambda.DockerImageFunction(
            self, "MLInferenceFunction",
            function_name=f"{project_prefix}-{env_name}-ml-inference",
            code=_lambda.DockerImageCode.from_ecr(
                repository=ecr_repo,
                tag="latest",
            ),
            role=lambda_role,
            memory_size=2048,
            timeout=Duration.seconds(30),
            reserved_concurrent_executions=5,
            environment={
                "ENVIRONMENT": env_name,
                "PROJECT_PREFIX": project_prefix,
                "ANALYTICS_BUCKET": self.analytics_bucket.bucket_name,
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
            string_value=self.analytics_bucket.bucket_name,
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
            string_value=ecr_repo.repository_uri,
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
            value=ecr_repo.repository_uri,
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

        # SNS Topic for billing alerts (in us-east-1)
        topic = sns.Topic(self, "BillingAlertsTopic", topic_name="billing-alerts")
        topic.add_subscription(subs.EmailSubscription(billing_email))

        # AWS/Billing metric only exists in us-east-1
        total_cost_metric = cloudwatch.Metric(
            namespace="AWS/Billing",
            metric_name="EstimatedCharges",
            dimensions_map={"Currency": "USD"},
            period=Duration.hours(6),
            statistic="Maximum",
        )

        # Alarm at 80% of the monthly budget
        alarm = cloudwatch.Alarm(
            self,
            "MonthlySpend80Pct",
            metric=total_cost_metric,
            threshold=monthly_budget * 0.8,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )
        alarm.add_alarm_action(cloudwatch_actions.SnsAction(topic))

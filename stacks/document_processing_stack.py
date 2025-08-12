"""CDK Stack for Document Processing with OCR capabilities."""

from constructs import Construct
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_sqs as sqs,
    aws_glue as glue,
)

class DocumentProcessingStack(Stack):
    """CDK Stack for document processing infrastructure."""
    
    def __init__(self, scope: Construct, construct_id: str, *, project_prefix: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account = self.account
        region = self.region
        suffix = f"{account}-{region}".lower()

        # Reference existing buckets from foundation stack
        raw_bucket = s3.Bucket.from_bucket_name(
            self, "RawBucketRef", 
            f"{project_prefix}-raw-{env_name}-{suffix}"
        )
        processed_bucket = s3.Bucket.from_bucket_name(
            self, "ProcessedBucketRef", 
            f"{project_prefix}-processed-{env_name}-{suffix}"
        )
        analytics_bucket = s3.Bucket.from_bucket_name(
            self, "AnalyticsBucketRef", 
            f"{project_prefix}-analytics-{env_name}-{suffix}"
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
                raw_bucket.bucket_arn,
                f"{raw_bucket.bucket_arn}/*",
                processed_bucket.bucket_arn,
                f"{processed_bucket.bucket_arn}/*",
                analytics_bucket.bucket_arn,
                f"{analytics_bucket.bucket_arn}/*",
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
                "RAW_BUCKET": raw_bucket.bucket_name,
                "PROCESSED_BUCKET": processed_bucket.bucket_name,
                "ANALYTICS_BUCKET": analytics_bucket.bucket_name,
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

        # Configure S3 event notifications for document processing
        router_destination = s3n.LambdaDestination(document_router)
        
        # PDF files
        raw_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED_PUT,
            router_destination,
            s3.NotificationKeyFilter(prefix="docs/", suffix=".pdf")
        )
        raw_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED_PUT,
            router_destination,
            s3.NotificationKeyFilter(prefix="docs/", suffix=".PDF")
        )
        
        # DOCX files
        raw_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED_PUT,
            router_destination,
            s3.NotificationKeyFilter(prefix="docs/", suffix=".docx")
        )

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
                "RAW_BUCKET": raw_bucket.bucket_name,
                "PROCESSED_BUCKET": processed_bucket.bucket_name,
                "ANALYTICS_BUCKET": analytics_bucket.bucket_name,
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
                    path=f"s3://{processed_bucket.bucket_name}/docs/text/"
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
                    path=f"s3://{processed_bucket.bucket_name}/docs/metrics/"
                )]
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(
                recrawl_behavior="CRAWL_EVERYTHING"
            ),
        )


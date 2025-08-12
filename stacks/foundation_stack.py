from typing import List
from constructs import Construct
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
)

class FoundationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, project_prefix: str, env_name: str, billing_email: str, monthly_budget: float, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
        # Optional: API rate/insight selectors could be added later.

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
                name="legal_platform",
                description="Data catalog for legal compliance platform (Phase 0)",
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

        # ---------- Tags ----------
        for b in [self.raw_bucket, self.processed_bucket, self.analytics_bucket, self.audit_bucket]:
            Tags.of(b).add("Project", "LegalCompliance")
            Tags.of(b).add("Env", env_name)

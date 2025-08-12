from constructs import Construct
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
    aws_glue as glue,
    aws_s3_assets as assets,
)

class DataQualityStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, project_prefix: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account = self.account
        region = self.region
        suffix = f"{account}-{region}".lower()

        # Buckets from Phase 0
        raw_bucket       = s3.Bucket.from_bucket_name(self, "RawBucketRef",       f"{project_prefix}-raw-{env_name}-{suffix}")
        processed_bucket = s3.Bucket.from_bucket_name(self, "ProcessedBucketRef", f"{project_prefix}-processed-{env_name}-{suffix}")
        analytics_bucket = s3.Bucket.from_bucket_name(self, "AnalyticsBucketRef", f"{project_prefix}-analytics-{env_name}-{suffix}")

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
                raw_bucket.bucket_arn,
                processed_bucket.bucket_arn,
                analytics_bucket.bucket_arn,
            ],
        ))
        glue_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetObject","s3:PutObject","s3:DeleteObject"],
            resources=[
                f"{raw_bucket.bucket_arn}/*",
                f"{processed_bucket.bucket_arn}/*",
                f"{analytics_bucket.bucket_arn}/*",
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
                    path=f"s3://{raw_bucket.bucket_name}/{raw_prefix}"
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
                    path=f"s3://{processed_bucket.bucket_name}/{processed_prefix}"
                )]
            ),
            schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                delete_behavior="LOG", update_behavior="UPDATE_IN_DATABASE"
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(recrawl_behavior="CRAWL_EVERYTHING"),
        )

        # ---- Glue ETL Job asset (PySpark script) ----
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
                "--raw_bucket": raw_bucket.bucket_name,
                "--processed_bucket": processed_bucket.bucket_name,
                "--raw_prefix": raw_prefix,
                "--processed_prefix": processed_prefix,
                "--TempDir": f"s3://{analytics_bucket.bucket_name}/glue-tmp/"
            },
            execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=1),
            description="ETL: Clean contract register CSV -> Parquet with basic remediation",
        )

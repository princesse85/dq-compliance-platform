
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_ecr as ecr,
)
from constructs import Construct

class EcrStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, project_prefix: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.ecr_repo = ecr.Repository(
            self, "MLInferenceECRRepo",
            repository_name=f"{project_prefix}-{env_name}-ml-inference-repo",
            image_scan_on_push=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
        )

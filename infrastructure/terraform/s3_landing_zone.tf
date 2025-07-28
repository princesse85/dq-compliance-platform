terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~>5.0" }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "raw_landing" {
  bucket = "${var.project_id}-raw"
  force_destroy = true
  tags = {
    Project = var.project_id
    Layer   = "raw"
  }
}

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.85.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "dev_data_lake" {
  source      = "../../02_builds/tf_modules/s3_lake"
  bucket_name = "${var.data_lake_bucket_prefix}-${var.environment}-${var.aws_region}"
  environment = var.environment
}

output "data_lake_bucket_id" {
  value       = module.dev_data_lake.bucket_id
  description = "Provisioned S3 Data Lake Bucket Identifier"
}

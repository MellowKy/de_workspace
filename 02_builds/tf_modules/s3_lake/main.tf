terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "bucket_name" {
  type        = string
  description = "Name of the S3 Data Lake bucket"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Deployment environment (dev/prod)"
}

resource "aws_s3_bucket" "data_lake" {
  bucket        = var.bucket_name
  force_destroy = var.environment == "dev" ? true : false

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Layer       = "DataLake"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lake_encryption" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "lake_security" {
  bucket                  = aws_s3_bucket.data_lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "lake_lifecycle" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    id     = "archive_raw_logs"
    status = "Enabled"

    filter {
      prefix = "raw/"
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

output "bucket_arn" {
  value = aws_s3_bucket.data_lake.arn
}

output "bucket_id" {
  value = aws_s3_bucket.data_lake.id
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target AWS deployment region"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Target execution environment (dev/staging/prod)"
}

variable "data_lake_bucket_prefix" {
  type        = string
  default     = "enterprise-data-lake"
  description = "Prefix for S3 Data Lake naming convention"
}

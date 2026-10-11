variable "bucket_name" {
  description = "Name of the S3 data lake bucket"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, ci, prod)"
  type        = string
  default     = "dev"
}

output "bucket_id" {
  description = "The ID/Name of the S3 bucket"
  value       = aws_s3_bucket.lake.id
}

output "bucket_arn" {
  description = "The ARN of the S3 bucket"
  value       = aws_s3_bucket.lake.arn
}

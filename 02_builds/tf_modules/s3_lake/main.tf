resource "aws_s3_bucket" "lake" {
  bucket        = var.bucket_name
  force_destroy = var.environment == "ci" ? true : false

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Security    = "Encrypted-Private"
  }
}

resource "aws_s3_bucket_public_access_block" "lake_public_block" {
  bucket                  = aws_s3_bucket.lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lake_encryption" {
  bucket = aws_s3_bucket.lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "lake_ownership" {
  bucket = aws_s3_bucket.lake.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

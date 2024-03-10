provider "aws" {
 region = "us-west-2" # Specify your AWS region
}

# Kinesis Stream
resource "aws_kinesis_stream" "event_stream" {
 name             = "event-stream"
 shard_count      = 1
 retention_period = 24
}

# S3 Bucket for Data Lake
resource "aws_s3_bucket" "data_lake" {
 bucket = "babbel-data-lake-bucket"
 acl    = "private"
}

# IAM Role for Lambda Function
resource "aws_iam_role" "lambda_role" {
 name = "lambda-role"
 assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
 })
}

# IAM Policy for Lambda Function
resource "aws_iam_role_policy" "lambda_policy" {
 name = "lambda-policy"
 role = aws_iam_role.lambda_role.id
 policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.data_lake.arn}/*"
      }
    ]
 })
}

# Lambda Function
data "archive_file" "lambda_zip" {
 type        = "zip"
 source_dir = "${path.module}/lambda.py"
 output_path = "${path.module}/lambda_function_payload.zip"
}

resource "aws_lambda_function" "lambda_function" {
 function_name = "babbel-event-processor"
 handler       = "lambda_function.lambda_handler"
 runtime       = "python3.8"
 role          = aws_iam_role.lambda_role.arn
 filename      = data.archive_file.lambda_zip.output_path
 source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)
}

# Event Source Mapping
resource "aws_lambda_event_source_mapping" "event_source_mapping" {
 event_source_arn = aws_kinesis_stream.event_stream.arn
 function_name     = aws_lambda_function.lambda_function.function_name
 starting_position = "TRIM_HORIZON"
}

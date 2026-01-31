# Lambda Execution Role
resource "aws_iam_role" "lambda_execution" {
  name = local.lambda_execution_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name = "Lambda Execution Role"
    }
  )
}

# Attach basic Lambda execution role (CloudWatch Logs)
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DynamoDB Access Policy
resource "aws_iam_role_policy" "dynamodb_access" {
  name = "${local.resource_prefix}-dynamodb-access"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:UpdateItem"
        ]
        Resource = [
          aws_dynamodb_table.model_registry.arn,
          aws_dynamodb_table.model_predictions.arn
        ]
      }
    ]
  })
}

# CloudWatch Metrics Policy
resource "aws_iam_role_policy" "cloudwatch_metrics" {
  name = "${local.resource_prefix}-cloudwatch-metrics"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      }
    ]
  })
}

# S3 Access Policy for Model Loading
resource "aws_iam_role_policy" "s3_model_access" {
  name = "${local.resource_prefix}-s3-model-access"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.lambda_code_bucket}",
          "arn:aws:s3:::${var.lambda_code_bucket}/*"
        ]
      }
    ]
  })
}

# DynamoDB Table Outputs
output "model_registry_table_name" {
  description = "Name of the model registry DynamoDB table"
  value       = aws_dynamodb_table.model_registry.name
}

output "model_registry_table_arn" {
  description = "ARN of the model registry DynamoDB table"
  value       = aws_dynamodb_table.model_registry.arn
}

output "model_predictions_table_name" {
  description = "Name of the model predictions DynamoDB table"
  value       = aws_dynamodb_table.model_predictions.name
}

output "model_predictions_table_arn" {
  description = "ARN of the model predictions DynamoDB table"
  value       = aws_dynamodb_table.model_predictions.arn
}

# Lambda Function Outputs
output "classify_anomaly_function_arn" {
  description = "ARN of the classify_anomaly Lambda function"
  value       = aws_lambda_function.classify_anomaly.arn
}

output "classify_anomaly_function_name" {
  description = "Name of the classify_anomaly Lambda function"
  value       = aws_lambda_function.classify_anomaly.function_name
}

output "classify_anomaly_function_url" {
  description = "Direct URL of the classify_anomaly Lambda function"
  value       = var.enable_function_urls ? aws_lambda_function_url.classify_anomaly[0].function_url : null
}

output "classify_level_function_arn" {
  description = "ARN of the classify_level Lambda function"
  value       = aws_lambda_function.classify_level.arn
}

output "classify_level_function_name" {
  description = "Name of the classify_level Lambda function"
  value       = aws_lambda_function.classify_level.function_name
}

output "classify_level_function_url" {
  description = "Direct URL of the classify_level Lambda function"
  value       = var.enable_function_urls ? aws_lambda_function_url.classify_level[0].function_url : null
}

# IAM Role Outputs
output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution.arn
}

output "lambda_execution_role_name" {
  description = "Name of the Lambda execution role"
  value       = aws_iam_role.lambda_execution.name
}

# S3 Bucket Outputs
output "lambda_code_bucket" {
  description = "Name of the S3 bucket for Lambda code"
  value       = var.lambda_code_bucket
}

# API Gateway Outputs
output "rest_api_id" {
  description = "ID of the REST API"
  value       = var.enable_api_gateway ? aws_api_gateway_rest_api.mlops[0].id : null
}

output "rest_api_endpoint_base" {
  description = "Base URL of the REST API"
  value = var.enable_api_gateway ? format(
    "https://%s.execute-api.localhost.localstack.cloud:4566/%s",
    aws_api_gateway_rest_api.mlops[0].id,
    var.stage
  ) : null
}

output "rest_api_anomaly_endpoint" {
  description = "Endpoint for anomaly classification via API Gateway"
  value = var.enable_api_gateway ? format(
    "https://%s.execute-api.localhost.localstack.cloud:4566/%s/anomaly",
    aws_api_gateway_rest_api.mlops[0].id,
    var.stage
  ) : null
}

output "rest_api_level_endpoint" {
  description = "Endpoint for level classification via API Gateway"
  value = var.enable_api_gateway ? format(
    "https://%s.execute-api.localhost.localstack.cloud:4566/%s/level",
    aws_api_gateway_rest_api.mlops[0].id,
    var.stage
  ) : null
}

# CloudWatch Outputs
output "cloudwatch_dashboard_url" {
  description = "URL to the CloudWatch dashboard"
  value = format(
    "https://console.aws.amazon.com/cloudwatch/home?region=%s#dashboards:name=%s",
    data.aws_region.current.name,
    aws_cloudwatch_dashboard.anomaly_classifier.dashboard_name
  )
}

# Project Information
output "project_stage" {
  description = "Current deployment stage"
  value       = var.stage
}

output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = data.aws_region.current.name
}

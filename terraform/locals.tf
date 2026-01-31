locals {
  # Project naming
  project_name = "mlops-sandbox"

  # Resource naming with stage
  resource_prefix = "${local.project_name}-${var.stage}"

  # Common tags for all resources
  common_tags = merge(
    {
      Project     = local.project_name
      Stage       = var.stage
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    },
    var.tags
  )

  # DynamoDB table names
  model_registry_table_name    = "model-registry"
  model_predictions_table_name = "model-predictions"

  # Lambda function names
  classify_anomaly_function_name = "classify_anomaly"
  classify_level_function_name   = "classify_level"

  # IAM role name
  lambda_execution_role_name = "${local.resource_prefix}-lambda-execution-role"

  # API Gateway
  api_gateway_name = "${local.resource_prefix}-api"

  # CloudWatch
  dashboard_name = "MLOpsSandbox-AnomalyClassifier"

  # Lambda code keys in S3
  classify_anomaly_s3_key = "classify_anomaly.zip"
  classify_level_s3_key   = "classify_level.zip"
}

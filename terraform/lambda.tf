# Classify Anomaly Lambda Function
resource "aws_lambda_function" "classify_anomaly" {
  function_name = local.classify_anomaly_function_name
  role          = aws_iam_role.lambda_execution.arn
  handler       = "handler.handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout

  s3_bucket = var.lambda_code_bucket
  s3_key    = local.classify_anomaly_s3_key

  environment {
    variables = {
      STAGE                  = var.stage
      MODEL_REGISTRY_TABLE   = aws_dynamodb_table.model_registry.name
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.dynamodb_access,
    aws_iam_role_policy.cloudwatch_metrics,
  ]

  tags = merge(
    local.common_tags,
    {
      Name = "Classify Anomaly Function"
    }
  )
}

# Classify Level Lambda Function
resource "aws_lambda_function" "classify_level" {
  function_name = local.classify_level_function_name
  role          = aws_iam_role.lambda_execution.arn
  handler       = "handler.handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout

  s3_bucket = var.lambda_code_bucket
  s3_key    = local.classify_level_s3_key

  environment {
    variables = {
      STAGE                  = var.stage
      MODEL_REGISTRY_TABLE   = aws_dynamodb_table.model_registry.name
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.dynamodb_access,
    aws_iam_role_policy.cloudwatch_metrics,
  ]

  tags = merge(
    local.common_tags,
    {
      Name = "Classify Level Function"
    }
  )
}

# Lambda Function URLs (if enabled)
resource "aws_lambda_function_url" "classify_anomaly" {
  count              = var.enable_function_urls ? 1 : 0
  function_name      = aws_lambda_function.classify_anomaly.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST"]
    allow_headers = ["Content-Type"]
  }
}

resource "aws_lambda_function_url" "classify_level" {
  count              = var.enable_function_urls ? 1 : 0
  function_name      = aws_lambda_function.classify_level.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST"]
    allow_headers = ["Content-Type"]
  }
}

# Lambda permissions for Function URLs
resource "aws_lambda_permission" "classify_anomaly_url" {
  count              = var.enable_function_urls ? 1 : 0
  statement_id       = "AllowFunctionUrlInvoke"
  action             = "lambda:InvokeFunctionUrl"
  function_name      = aws_lambda_function.classify_anomaly.function_name
  principal          = "*"
  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "classify_level_url" {
  count              = var.enable_function_urls ? 1 : 0
  statement_id       = "AllowFunctionUrlInvoke"
  action             = "lambda:InvokeFunctionUrl"
  function_name      = aws_lambda_function.classify_level.function_name
  principal          = "*"
  function_url_auth_type = "NONE"
}

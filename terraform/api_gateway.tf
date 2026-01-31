# REST API
resource "aws_api_gateway_rest_api" "mlops" {
  count       = var.enable_api_gateway ? 1 : 0
  name        = local.api_gateway_name
  description = "REST API for MLOps Lambda functions with path-based routing"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "MLOps REST API"
    }
  )
}

# Anomaly Resource
resource "aws_api_gateway_resource" "anomaly" {
  count       = var.enable_api_gateway ? 1 : 0
  rest_api_id = aws_api_gateway_rest_api.mlops[0].id
  parent_id   = aws_api_gateway_rest_api.mlops[0].root_resource_id
  path_part   = "anomaly"
}

# Level Resource
resource "aws_api_gateway_resource" "level" {
  count       = var.enable_api_gateway ? 1 : 0
  rest_api_id = aws_api_gateway_rest_api.mlops[0].id
  parent_id   = aws_api_gateway_rest_api.mlops[0].root_resource_id
  path_part   = "level"
}

# Anomaly POST Method
resource "aws_api_gateway_method" "anomaly_post" {
  count            = var.enable_api_gateway ? 1 : 0
  rest_api_id      = aws_api_gateway_rest_api.mlops[0].id
  resource_id      = aws_api_gateway_resource.anomaly[0].id
  http_method      = "POST"
  authorization    = "NONE"
}

# Anomaly Integration
resource "aws_api_gateway_integration" "anomaly_integration" {
  count                   = var.enable_api_gateway ? 1 : 0
  rest_api_id             = aws_api_gateway_rest_api.mlops[0].id
  resource_id             = aws_api_gateway_resource.anomaly[0].id
  http_method             = aws_api_gateway_method.anomaly_post[0].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.classify_anomaly.invoke_arn
}

# Level POST Method
resource "aws_api_gateway_method" "level_post" {
  count            = var.enable_api_gateway ? 1 : 0
  rest_api_id      = aws_api_gateway_rest_api.mlops[0].id
  resource_id      = aws_api_gateway_resource.level[0].id
  http_method      = "POST"
  authorization    = "NONE"
}

# Level Integration
resource "aws_api_gateway_integration" "level_integration" {
  count                   = var.enable_api_gateway ? 1 : 0
  rest_api_id             = aws_api_gateway_rest_api.mlops[0].id
  resource_id             = aws_api_gateway_resource.level[0].id
  http_method             = aws_api_gateway_method.level_post[0].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.classify_level.invoke_arn
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "mlops" {
  count       = var.enable_api_gateway ? 1 : 0
  rest_api_id = aws_api_gateway_rest_api.mlops[0].id

  depends_on = [
    aws_api_gateway_integration.anomaly_integration,
    aws_api_gateway_integration.level_integration,
  ]
}

# API Gateway Stage
resource "aws_api_gateway_stage" "mlops" {
  count         = var.enable_api_gateway ? 1 : 0
  deployment_id = aws_api_gateway_deployment.mlops[0].id
  rest_api_id   = aws_api_gateway_rest_api.mlops[0].id
  stage_name    = var.stage
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "api_gateway_anomaly" {
  count       = var.enable_api_gateway ? 1 : 0
  statement_id = "AllowAPIGatewayInvoke"
  action       = "lambda:InvokeFunction"
  function_name = aws_lambda_function.classify_anomaly.function_name
  principal    = "apigateway.amazonaws.com"
  source_arn   = "${aws_api_gateway_rest_api.mlops[0].execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_level" {
  count       = var.enable_api_gateway ? 1 : 0
  statement_id = "AllowAPIGatewayInvoke"
  action       = "lambda:InvokeFunction"
  function_name = aws_lambda_function.classify_level.function_name
  principal    = "apigateway.amazonaws.com"
  source_arn   = "${aws_api_gateway_rest_api.mlops[0].execution_arn}/*/*"
}

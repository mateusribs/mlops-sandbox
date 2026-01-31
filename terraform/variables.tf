variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "stage" {
  description = "Deployment stage (local, dev, prod)"
  type        = string
  default     = "local"

  validation {
    condition     = contains(["local", "dev", "prod"], var.stage)
    error_message = "Stage must be one of: local, dev, prod"
  }
}

variable "use_localstack" {
  description = "Use LocalStack for local development"
  type        = bool
  default     = true
}

variable "lambda_code_bucket" {
  description = "S3 bucket name for Lambda deployment packages"
  type        = string
  default     = "lambda-deployments"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 10

  validation {
    condition     = var.lambda_timeout > 0 && var.lambda_timeout <= 20
    error_message = "Lambda timeout must be between 1 and 20 seconds"
  }
}

variable "lambda_runtime" {
  description = "Lambda runtime version"
  type        = string
  default     = "python3.13"
}

variable "enable_function_urls" {
  description = "Enable direct Lambda Function URLs"
  type        = bool
  default     = true
}

variable "enable_api_gateway" {
  description = "Enable API Gateway endpoints"
  type        = bool
  default     = true
}

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PAY_PER_REQUEST or PROVISIONED)"
  type        = string
  default     = "PAY_PER_REQUEST"

  validation {
    condition     = contains(["PAY_PER_REQUEST", "PROVISIONED"], var.dynamodb_billing_mode)
    error_message = "Billing mode must be either PAY_PER_REQUEST or PROVISIONED"
  }
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

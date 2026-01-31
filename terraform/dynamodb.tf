# Model Registry Table
resource "aws_dynamodb_table" "model_registry" {
  name           = local.model_registry_table_name
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "model_name"
  range_key      = "version"

  attribute {
    name = "model_name"
    type = "S"
  }

  attribute {
    name = "version"
    type = "S"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Model Registry"
    }
  )
}

# Model Predictions Table
resource "aws_dynamodb_table" "model_predictions" {
  name           = local.model_predictions_table_name
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "model_name"
  range_key      = "timestamp"

  attribute {
    name = "model_name"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Model Predictions"
    }
  )
}

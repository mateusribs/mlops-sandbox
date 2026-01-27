#!/bin/bash

LAMBDAS_PATH="src/lambdas"

export AWS_DEFAULT_REGION=us-east-1

# Create DynamoDB Model Registry Table
echo "Creating DynamoDB model registry table..."
awslocal dynamodb create-table \
    --table-name model-registry \
    --attribute-definitions \
        AttributeName=model_name,AttributeType=S \
        AttributeName=version,AttributeType=S \
    --key-schema \
        AttributeName=model_name,KeyType=HASH \
        AttributeName=version,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    2>/dev/null || echo "Table model-registry already exists"

awslocal dynamodb wait table-exists --table-name model-registry

echo "Model registry table 'model-registry' is ready."
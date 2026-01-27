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

echo "Creating DynamoDB predictions table..."

awslocal dynamodb create-table \
    --table-name model-predictions \
    --attribute-definitions \
        AttributeName=model_name,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=model_name,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    2>/dev/null || echo "Table model-predictions already exists"

awslocal dynamodb wait table-exists --table-name model-predictions

echo "Predictions table 'model-predictions' is ready."

# Deploy Lambda Functions
echo "Building and deploying Lambda functions..."

(cd $LAMBDAS_PATH/classify_anomaly; rm -f lambda.zip; zip lambda.zip handler.py)
(cd $LAMBDAS_PATH/classify_level; rm -f lambda.zip; zip lambda.zip handler.py)

# Lambda will fail if version doesn't exist in registry
# Overwrite lambda function if it already exists
awslocal lambda create-function \
    --function-name classify_anomaly \
    --runtime python3.11 \
    --timeout 10 \
    --zip-file fileb://$LAMBDAS_PATH/classify_anomaly/lambda.zip \
    --handler handler.handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{STAGE=local,MODEL_REGISTRY_TABLE=model-registry}" \
    2>/dev/null || {
        echo "Function exists, updating..."
        awslocal lambda update-function-code \
            --function-name classify_anomaly \
            --zip-file fileb://$LAMBDAS_PATH/classify_anomaly/lambda.zip
        
        awslocal lambda update-function-configuration \
            --function-name classify_anomaly \
            --runtime python3.11 \
            --timeout 10 \
            --handler handler.handler \
            --environment Variables="{STAGE=local,MODEL_REGISTRY_TABLE=model-registry}"
    }

awslocal lambda wait function-active-v2 --function-name classify_anomaly

awslocal lambda create-function-url-config \
    --function-name classify_anomaly \
    --auth-type NONE \
    2>/dev/null || echo "Function URL config for classify_anomaly already exists"

awslocal lambda create-function \
    --function-name classify_level \
    --runtime python3.11 \
    --timeout 10 \
    --zip-file fileb://$LAMBDAS_PATH/classify_level/lambda.zip \
    --handler handler.handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{STAGE=local,MODEL_REGISTRY_TABLE=model-registry}" \
    2>/dev/null || {
        echo "Function exists, updating..."
        awslocal lambda update-function-code \
            --function-name classify_level \
            --zip-file fileb://$LAMBDAS_PATH/classify_level/lambda.zip
        
        awslocal lambda update-function-configuration \
            --function-name classify_level \
            --runtime python3.11 \
            --timeout 10 \
            --handler handler.handler \
            --environment Variables="{STAGE=local,MODEL_REGISTRY_TABLE=model-registry}"
    }

awslocal lambda wait function-active-v2 --function-name classify_level

awslocal lambda create-function-url-config \
    --function-name classify_level \
    --auth-type NONE \
    2>/dev/null || echo "Function URL config for classify_level already exists"

echo
echo "Fetching function URL for 'classify_anomaly' Lambda..."
awslocal lambda list-function-url-configs --function-name classify_anomaly --output json | jq -r '.FunctionUrlConfigs[0].FunctionUrl'
echo "Fetching function URL for 'classify_level' Lambda..."
awslocal lambda list-function-url-configs --function-name classify_level --output json | jq -r '.FunctionUrlConfigs[0].FunctionUrl'
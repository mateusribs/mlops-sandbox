#!/bin/bash

set -e

LAMBDAS_PATH="src/lambdas"
STACK_NAME="mlops-sandbox-stack"
S3_BUCKET="lambda-deployments"
CFN_TEMPLATE="cloudformation/infrastructure.json"

export AWS_DEFAULT_REGION=us-east-1

echo "MLOps Sandbox Infrastructure Deployment"

echo "Creating S3 bucket for Lambda deployments"
awslocal s3 mb s3://$S3_BUCKET 2>/dev/null || echo "Bucket $S3_BUCKET already exists"

echo "Building Lambda functions..."
(
  cd $LAMBDAS_PATH/classify_anomaly
  rm -f lambda.zip
  zip -q lambda.zip handler.py
)
(
  cd $LAMBDAS_PATH/classify_level
  rm -f lambda.zip
  zip -q lambda.zip handler.py
)
echo "Lambda zip files created."

echo "Uploading Lambda functions to S3..."
awslocal s3 cp $LAMBDAS_PATH/classify_anomaly/lambda.zip s3://$S3_BUCKET/classify_anomaly.zip
awslocal s3 cp $LAMBDAS_PATH/classify_level/lambda.zip s3://$S3_BUCKET/classify_level.zip
echo "Lambda functions uploaded."

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
awslocal cloudformation deploy \
  --stack-name $STACK_NAME \
  --template-file $CFN_TEMPLATE \
  --parameter-overrides \
  Stage=local \
  LambdaCodeBucket=$S3_BUCKET \
  --capabilities CAPABILITY_NAMED_IAM

echo ""
echo "Waiting for stack to be ready..."
awslocal cloudformation wait stack-create-complete --stack-name $STACK_NAME 2>/dev/null ||
  awslocal cloudformation wait stack-update-complete --stack-name $STACK_NAME 2>/dev/null || true

echo "Stack Outputs:"
awslocal cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table

echo "Function URLs:"
CLASSIFY_ANOMALY_URL=$(awslocal cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ClassifyAnomalyFunctionUrl`].OutputValue' --output text)
CLASSIFY_LEVEL_URL=$(awslocal cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ClassifyLevelFunctionUrl`].OutputValue' --output text)

echo "classify_anomaly: $CLASSIFY_ANOMALY_URL"
echo "classify_level:   $CLASSIFY_LEVEL_URL"

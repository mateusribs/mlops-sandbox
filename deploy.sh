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
  rm -rf packages lambda.zip
  mkdir -p packages
  pip install --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.13 --target packages/ -r requirements.txt
  zip -q lambda.zip handler.py
  cd packages
  zip -qr ../lambda.zip .
)
(
  cd $LAMBDAS_PATH/classify_level
  rm -rf packages lambda.zip
  pip install --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.13 --target packages/ -r requirements.txt
  zip -q lambda.zip handler.py
  cd packages
  zip -qr ../lambda.zip .
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

echo "Waiting for stack to be ready..."
awslocal cloudformation wait stack-create-complete --stack-name $STACK_NAME 2>/dev/null ||
  awslocal cloudformation wait stack-update-complete --stack-name $STACK_NAME 2>/dev/null || true

make train-models

echo "Stack Outputs:"
awslocal cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table

echo "API Gateway Endpoints"
ANOMALY_ENDPOINT=$(awslocal cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`RestApiAnomalyEndpoint`].OutputValue' --output text)
LEVEL_ENDPOINT=$(awslocal cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`RestApiLevelEndpoint`].OutputValue' --output text)

echo "Anomaly Classification: $ANOMALY_ENDPOINT"
echo "Level Classification:   $LEVEL_ENDPOINT"

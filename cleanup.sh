#!/bin/bash

set -e

STACK_NAME="mlops-sandbox-stack"
S3_BUCKET="lambda-deployments"

export AWS_DEFAULT_REGION=us-east-1

echo "Cleaning up MLOps Sandbox Infrastructure"

echo "Deleting CloudFormation stack..."
awslocal cloudformation delete-stack --stack-name $STACK_NAME

echo "Waiting for stack deletion to complete..."
awslocal cloudformation wait stack-delete-complete --stack-name $STACK_NAME 2>/dev/null || true

echo "Stack deleted successfully."

echo "Deleting S3 bucket and contents..."
awslocal s3 rb s3://$S3_BUCKET --force 2>/dev/null || echo "Bucket already deleted or doesn't exist"

echo "Cleanup Complete!"

#!/bin/bash

set -e

LAMBDAS_PATH="src/lambdas"
TERRAFORM_DIR="terraform"
S3_BUCKET="lambda-deployments"

export AWS_DEFAULT_REGION="us-east-1"

# Step 1: Create S3 bucket
echo ""
echo "Step 1: Setting up S3 bucket"
if awslocal s3 ls "s3://$S3_BUCKET" 2>/dev/null; then
  echo "  Bucket $S3_BUCKET already exists, skipping creation"
else
  awslocal s3 mb s3://$S3_BUCKET
  echo "  Bucket created"
fi

# Step 2: Build Lambda functions
echo ""
echo "Step 2: Building Lambda functions"

echo "  Building classify_anomaly..."
(
  cd $LAMBDAS_PATH/classify_anomaly
  rm -rf packages lambda.zip
  mkdir -p packages
  pip install -q --target packages/ -r requirements.txt 2>/dev/null || pip install --target packages/ -r requirements.txt
  zip -q lambda.zip handler.py
  if [ -d "packages" ] && [ "$(ls -A packages)" ]; then
    cd packages && zip -qr ../lambda.zip . 2>/dev/null || true && cd ..
  fi
)
echo "  classify_anomaly built"

echo "  Building classify_level..."
(
  cd $LAMBDAS_PATH/classify_level
  rm -rf packages lambda.zip
  mkdir -p packages
  pip install -q --target packages/ -r requirements.txt 2>/dev/null || pip install --target packages/ -r requirements.txt
  zip -q lambda.zip handler.py
  if [ -d "packages" ] && [ "$(ls -A packages)" ]; then
    cd packages && zip -qr ../lambda.zip . 2>/dev/null || true && cd ..
  fi
)
echo "  classify_level built"

# Step 3: Upload to S3
echo ""
echo "Step 3: Uploading Lambda functions to S3"
awslocal s3 cp $LAMBDAS_PATH/classify_anomaly/lambda.zip s3://$S3_BUCKET/classify_anomaly.zip
awslocal s3 cp $LAMBDAS_PATH/classify_level/lambda.zip s3://$S3_BUCKET/classify_level.zip
echo "  Lambda functions uploaded"

# Step 4: Deploy with Terraform
echo ""
echo "Step 4: Deploying infrastructure with Terraform"

cd $TERRAFORM_DIR || { echo "ERROR: Terraform directory not found"; exit 1; }

echo "  Initializing Terraform..."
tflocal init

echo "  Validating configuration..."
tflocal validate || { echo "ERROR: Terraform validation failed"; exit 1; }

echo "  Planning deployment..."
tflocal plan -var stage=local -var use_localstack=true -out=tfplan || { echo "ERROR: Terraform plan failed"; exit 1; }

echo "  Applying configuration..."
tflocal apply tfplan || { echo "ERROR: Terraform apply failed"; exit 1; }

# Step 5: Display outputs
echo ""
echo "Step 5: Deployment Summary"
echo ""
tflocal output

# Step 6: Display endpoints
echo ""
echo "API Endpoints:"
ANOMALY=$(tflocal output -raw rest_api_anomaly_endpoint 2>/dev/null || echo "Not available")
LEVEL=$(tflocal output -raw rest_api_level_endpoint 2>/dev/null || echo "Not available")
echo "  Anomaly: $ANOMALY"
echo "  Level:   $LEVEL"

# Step 7: Train models
echo ""
echo "Step 6: Training ML models"
cd ../
make train-models || echo "Model training skipped or failed (non-critical)"
cd terraform

echo ""
echo "Deployment completed successfully!"
echo ""

# Cleanup
rm -f tfplan
cd - > /dev/null

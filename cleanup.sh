#!/bin/bash

set -e

TERRAFORM_DIR="terraform"
S3_BUCKET="lambda-deployments"
LAMBDAS_PATH="src/lambdas"

export AWS_DEFAULT_REGION="us-east-1"

echo "Cleaning up MLOps Sandbox Infrastructure"
echo "========================================"

# Step 1: Destroy Terraform infrastructure
echo ""
echo "Step 1: Destroying Terraform-managed infrastructure..."

cd $TERRAFORM_DIR || { echo "ERROR: Terraform directory not found"; exit 1; }

echo "  Destroying all resources..."
tflocal destroy -var stage=local -var use_localstack=true -auto-approve || { echo "WARNING: Terraform destroy encountered issues"; }

echo "  ✓ Terraform resources destroyed"

cd - > /dev/null

# Step 2: Delete S3 bucket and contents
echo ""
echo "Step 2: Deleting S3 bucket and contents..."
awslocal s3 rb s3://$S3_BUCKET --force 2>/dev/null || echo "  Bucket already deleted or doesn't exist"
echo "  ✓ S3 bucket cleaned"

# Step 3: Clean local Lambda build artifacts
echo ""
echo "Step 3: Cleaning local Lambda build artifacts..."

for lambda_dir in $LAMBDAS_PATH/*/; do
  if [ -d "$lambda_dir" ]; then
    echo "  Cleaning $(basename $lambda_dir)..."
    rm -rf "$lambda_dir/packages" "$lambda_dir/lambda.zip"
  fi
done

echo "  ✓ Local artifacts cleaned"

# Step 4: Clean Terraform state and lock files (optional, for complete reset)
echo ""
echo "Step 4: Cleaning Terraform state..."

cd $TERRAFORM_DIR || { echo "ERROR: Terraform directory not found"; exit 1; }

rm -f terraform.tfstate terraform.tfstate.backup .terraform.lock.hcl
rm -rf .terraform

echo "  ✓ Terraform state cleaned"

cd - > /dev/null

echo ""
echo "✓ Cleanup completed successfully!"
echo ""

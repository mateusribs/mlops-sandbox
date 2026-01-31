#!/bin/bash

set -e

TERRAFORM_DIR="terraform"

export AWS_DEFAULT_REGION="us-east-1"

# Get base URL from Terraform outputs
echo "Retrieving API endpoint from Terraform..."
BASE_URL=$(cd $TERRAFORM_DIR && tflocal output -raw rest_api_endpoint_base)
echo "Base URL: $BASE_URL"
echo ""

uv run locust -f tests/load_tests/locustfile.py --host $BASE_URL

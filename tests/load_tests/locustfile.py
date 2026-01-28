import json
import os
import random
import sys
from datetime import UTC, datetime

import boto3
from dotenv import load_dotenv
from locust import TaskSet, User, between, task

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from tests.load_tests.config import LAMBDA_FUNCTIONS, LOAD_TEST_CONFIG

load_dotenv()


class LambdaTasks(TaskSet):
    """Task set for Lambda invocations."""

    def on_start(self):
        """Initialize Lambda client."""
        self.lambda_client = boto3.client(
            "lambda",
            endpoint_url=os.environ["LOCALSTACK_ENDPOINT_URL"],
            aws_access_key_id=os.environ["LOCALSTACK_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["LOCALSTACK_SECRET_ACCESS_KEY"],
            region_name=os.environ["LOCALSTACK_REGION_NAME"],
        )

    def _generate_payload(self, lambda_config: dict) -> dict:
        """Generate random test payload."""
        value_min, value_max = LOAD_TEST_CONFIG["value_range"]
        return {
            "model_name": lambda_config["model_name"],
            "model_version": lambda_config["model_version"],
            "value": random.uniform(value_min, value_max),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    @task(1)
    def invoke_classify_anomaly(self):
        """Task: Invoke classify_anomaly Lambda function."""
        payload = self._generate_payload(LAMBDA_FUNCTIONS["classify_anomaly"])
        try:
            response = self.lambda_client.invoke(
                FunctionName="classify_anomaly",
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )
            result = json.loads(response["Payload"].read())
            if result.get("statusCode") == 200:
                self.user.environment.events.request.fire(
                    request_type="lambda",
                    name="classify_anomaly",
                    response_time=0,
                    response_length=len(json.dumps(result)),
                    exception=None,
                    context={},
                )
            else:
                error = result.get("body", {}).get("error", "Unknown error")
                self.user.environment.events.request.fire(
                    request_type="lambda",
                    name="classify_anomaly",
                    response_time=0,
                    response_length=0,
                    exception=Exception(error),
                    context={},
                )
        except Exception as e:
            self.user.environment.events.request.fire(
                request_type="lambda",
                name="classify_anomaly",
                response_time=0,
                response_length=0,
                exception=e,
                context={},
            )

    @task(1)
    def invoke_classify_level(self):
        """Task: Invoke classify_level Lambda function."""
        payload = self._generate_payload(LAMBDA_FUNCTIONS["classify_level"])
        try:
            response = self.lambda_client.invoke(
                FunctionName="classify_level",
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )
            result = json.loads(response["Payload"].read())
            if result.get("statusCode") == 200:
                self.user.environment.events.request.fire(
                    request_type="lambda",
                    name="classify_level",
                    response_time=0,
                    response_length=len(json.dumps(result)),
                    exception=None,
                    context={},
                )
            else:
                error = result.get("body", {}).get("error", "Unknown error")
                self.user.environment.events.request.fire(
                    request_type="lambda",
                    name="classify_level",
                    response_time=0,
                    response_length=0,
                    exception=Exception(error),
                    context={},
                )
        except Exception as e:
            self.user.environment.events.request.fire(
                request_type="lambda",
                name="classify_level",
                response_time=0,
                response_length=0,
                exception=e,
                context={},
            )


class LambdaLoadTestUser(User):
    """Load test user that invokes Lambda functions."""

    tasks = [LambdaTasks]
    wait_time = between(1, 2)

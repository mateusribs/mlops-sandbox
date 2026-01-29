import os
import random
import sys
from datetime import datetime

from dotenv import load_dotenv
from locust import HttpUser, TaskSet, between, task

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from tests.load_tests.config import API_GATEWAY_CONFIG, LAMBDA_FUNCTIONS, LOAD_TEST_CONFIG

load_dotenv()


class APIGatewayTasks(TaskSet):
    """Task set for API Gateway HTTP requests."""

    def _generate_payload(self, lambda_config: dict) -> dict:
        """
        Generate random test payload for API requests.

        Args:
            lambda_config: Configuration dict with model details

        Returns:
            dict: Payload ready for HTTP POST request
        """
        value_min, value_max = LOAD_TEST_CONFIG["value_range"]
        return {
            "model_name": lambda_config["model_name"],
            "model_version": lambda_config["model_version"],
            "value": random.uniform(value_min, value_max),
            "timestamp": datetime.now().isoformat(),
        }

    @task(1)
    def invoke_classify_anomaly(self):
        """Task: Send HTTP POST request to /anomaly endpoint."""
        payload = self._generate_payload(LAMBDA_FUNCTIONS["classify_anomaly"])
        endpoint = API_GATEWAY_CONFIG["endpoints"]["classify_anomaly"]

        try:
            # Make HTTP POST request to API Gateway endpoint
            # Locust automatically records response time and status
            headers = {"Content-Type": "application/json"}

            response = self.client.post(
                endpoint,
                json=payload,
                headers=headers,
                name="classify_anomaly",  # Locust uses this for grouping results
                timeout=10,
            )

            # Check if response indicates success
            # Note: API Gateway returns 200 for successful invocations
            # Lambda errors are in the body with statusCode 500
            if response.status_code == 200:
                _ = response.json()
                # Log success to Locust
                self.user.environment.events.request.fire(
                    request_type="http",
                    name="classify_anomaly",
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=len(response.content),
                    exception=None,
                    context={},
                )
            else:
                # API Gateway returned error status code
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_body = response.json()
                    error_msg = error_body.get("body", {}).get("error", error_msg)
                except Exception as _:
                    error_msg = response.text or error_msg

                self.user.environment.events.request.fire(
                    request_type="http",
                    name="classify_anomaly",
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=0,
                    exception=Exception(error_msg),
                    context={},
                )
        except Exception as e:
            # Network error or request timeout
            self.user.environment.events.request.fire(
                request_type="http",
                name="classify_anomaly",
                response_time=0,
                response_length=0,
                exception=e,
                context={},
            )

    @task(1)
    def invoke_classify_level(self):
        """Task: Send HTTP POST request to /level endpoint."""
        payload = self._generate_payload(LAMBDA_FUNCTIONS["classify_level"])
        endpoint = API_GATEWAY_CONFIG["endpoints"]["classify_level"]

        try:
            # Make HTTP POST request to API Gateway endpoint
            # Locust automatically records response time and status
            headers = {"Content-Type": "application/json"}

            response = self.client.post(
                endpoint,
                json=payload,
                headers=headers,
                name="classify_level",  # Locust uses this for grouping results
                timeout=10,
            )

            # Check if response indicates success
            if response.status_code == 200:
                _ = response.json()
                # Log success to Locust
                self.user.environment.events.request.fire(
                    request_type="http",
                    name="classify_level",
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=len(response.content),
                    exception=None,
                    context={},
                )
            else:
                # API Gateway returned error status code
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_body = response.json()
                    error_msg = error_body.get("body", {}).get("error", error_msg)
                except Exception as _:
                    error_msg = response.text or error_msg

                self.user.environment.events.request.fire(
                    request_type="http",
                    name="classify_level",
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=0,
                    exception=Exception(error_msg),
                    context={},
                )
        except Exception as e:
            # Network error or request timeout
            self.user.environment.events.request.fire(
                request_type="http",
                name="classify_level",
                response_time=0,
                response_length=0,
                exception=e,
                context={},
            )


class APIGatewayLoadTestUser(HttpUser):
    """Load test user that makes HTTP requests to API Gateway."""

    # Tasks to execute
    tasks = [APIGatewayTasks]

    # Wait time between requests (1-2 seconds)
    wait_time = between(1, 2)

import os
import random
import sys
from datetime import datetime

from dotenv import load_dotenv
from locust import HttpUser, TaskSet, between, task

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from tests.load_tests.config import API_GATEWAY_CONFIG, LAMBDA_FUNCTIONS

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
        value_min, value_max = (0, 100)
        anomaly_prob = 0.05

        if random.random() < anomaly_prob:
            value = random.uniform(value_max * 3.5, value_max * 4.5)
        else:
            value = random.uniform(value_min, value_max)
        return {
            "model_name": lambda_config["model_name"],
            "model_version": lambda_config["model_version"],
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }

    @task(1)
    def invoke_classify_anomaly(self):
        """Task: Send HTTP POST request to /anomaly endpoint."""
        payload = self._generate_payload(LAMBDA_FUNCTIONS["classify_anomaly"])
        endpoint = API_GATEWAY_CONFIG["endpoints"]["classify_anomaly"]

        # Make HTTP POST request to API Gateway endpoint
        headers = {"Content-Type": "application/json"}

        _ = self.client.post(
            endpoint,
            json=payload,
            headers=headers,
            name="classify_anomaly",  # Locust uses this for grouping results
            timeout=10,
        )

    @task(1)
    def invoke_classify_level(self):
        """Task: Send HTTP POST request to /level endpoint."""
        payload = self._generate_payload(LAMBDA_FUNCTIONS["classify_level"])
        endpoint = API_GATEWAY_CONFIG["endpoints"]["classify_level"]

        # Make HTTP POST request to API Gateway endpoint
        headers = {"Content-Type": "application/json"}

        _ = self.client.post(
            endpoint,
            json=payload,
            headers=headers,
            name="classify_level",  # Locust uses this for grouping results
            timeout=10,
        )


class APIGatewayLoadTestUser(HttpUser):
    """Load test user that makes HTTP requests to API Gateway."""

    # Tasks to execute
    tasks = [APIGatewayTasks]

    # Wait time between requests (1-2 seconds)
    wait_time = between(1, 2)

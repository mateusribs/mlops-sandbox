import json
import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from functools import lru_cache

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver

logger = Logger(service="ClassifyAnomaly")
app = APIGatewayRestResolver()
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
cloudwatch = boto3.client("cloudwatch")

MODEL_REGISTRY_TABLE = os.environ.get("MODEL_REGISTRY_TABLE", "model-registry")


@dataclass
class DataPoint:
    value: float
    timestamp: str


class ToyAnomalyClassifier:
    def __init__(self, mean: float, std: float, threshold: float):
        self.mean = mean
        self.std = std
        self.threshold = threshold

    def predict(self, data_point: DataPoint) -> bool:
        return data_point.value > self.threshold


def get_model_metadata(model_name: str, model_version: str) -> dict:
    """
    Fetch model metadata from DynamoDB registry.

    Args:
        model_name (str): The name of the model.
        model_version (str): The version of the model.

    Returns:
        dict: The model metadata.
    """
    table = dynamodb.Table(MODEL_REGISTRY_TABLE)

    response = table.get_item(
        Key={"model_name": model_name, "version": model_version}, ConsistentRead=True
    )

    if "Item" not in response:
        raise ValueError(
            f"Model version not found: {model_name}@{model_version}. "
            f"Available versions can be queried in DynamoDB table: {MODEL_REGISTRY_TABLE}"
        )

    return response["Item"]


@lru_cache(maxsize=1)
def load_model(model_name: str, model_version: str) -> ToyAnomalyClassifier:
    """Load the anomaly classifier model from S3 based on metadata from DynamoDB.

    Args:
        model_name (str): The name of the model to load.
        model_version (str): The version of the model to load.
    Returns:
        ToyAnomalyClassifier: The loaded anomaly classifier model.
    """
    metadata = get_model_metadata(model_name, model_version)
    s3.download_file(metadata["s3_bucket"], metadata["s3_key"], "/tmp/model.json")

    with open("/tmp/model.json") as f:
        classifier_params = json.load(f)

    return ToyAnomalyClassifier(
        mean=classifier_params["mean"],
        std=classifier_params["std"],
        threshold=classifier_params["threshold"],
    )


def add_metric(metric_name: str, value: int) -> None:
    """Helper function to add custom CloudWatch metrics."""
    cloudwatch.put_metric_data(
        Namespace="ClassifyAnomaly",
        MetricData=[
            {
                "MetricName": metric_name,
                "Value": value,
                "Unit": "Count",
                "Dimensions": [{"Name": "service", "Value": "ClassifyAnomalyService"}],
            }
        ],
    )


@app.post("/anomaly")
def classify_anomaly():
    payload = app.current_event.json_body
    try:
        model_name = payload.get("model_name")
        model_version = payload.get("model_version")
        value = payload.get("value")
        timestamp = payload.get("timestamp")
    except KeyError as e:
        add_metric("MissingFieldError", 1)
        logger.exception(f"Missing required field in payload: {e}")
        return {"error": f"Missing required field: {str(e)}"}, 400

    try:
        model = load_model(model_name=model_name, model_version=model_version)
        data_point = DataPoint(value=value, timestamp=timestamp)
        is_anomaly = model.predict(data_point)
        add_metric("AnomalyDetected", int(is_anomaly))
        add_metric("TotalPredictions", 1)

        predictions_table = dynamodb.Table("model-predictions")
        predictions_table.put_item(
            Item={
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "version": model_version,
                "input": {"value": Decimal(str(value)), "timestamp": timestamp},
                "output": {"is_anomaly": is_anomaly},
            }
        )
        add_metric("PredictionPersisted", 1)
        logger.debug("Prediction persisted to DynamoDB")
        return {
            "is_anomaly": is_anomaly,
            "model_name": model_name,
            "model_version": model_version,
        }, 201
    except Exception as e:
        logger.exception(f"Error during prediction: {str(e)}")
        add_metric("PredictionError", 1)
        return {"error": "Internal server error"}, 500


@logger.inject_lambda_context
def handler(event, context):
    """AWS Lambda handler for classifying anomalies in time series data."""
    return app.resolve(event, context)

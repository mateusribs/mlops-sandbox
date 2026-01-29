import json
import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import boto3

classifier_params = None
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

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


def load_model(model_name: str, model_version: str) -> ToyAnomalyClassifier:
    """Load the anomaly classifier model from S3 based on metadata from DynamoDB.

    Args:
        model_name (str): The name of the model to load.
        model_version (str): The version of the model to load.
    Returns:
        ToyAnomalyClassifier: The loaded anomaly classifier model.
    """
    global classifier_params

    if classifier_params is None:
        metadata = get_model_metadata(model_name, model_version)
        s3.download_file(metadata["s3_bucket"], metadata["s3_key"], "/tmp/model.json")

        with open("/tmp/model.json") as f:
            classifier_params = json.load(f)

        print(f"Loaded model {model_name}@{model_version} from {metadata['s3_key']}")

    return ToyAnomalyClassifier(
        mean=classifier_params["mean"],
        std=classifier_params["std"],
        threshold=classifier_params["threshold"],
    )


def handler(event, context):
    """AWS Lambda handler for classifying anomalies in time series data.

    Args:
        event (dict): The event payload containing the data point to classify.
        context (LambdaContext): The runtime information of the Lambda function.

    Returns:
        dict: The classification result indicating if the data point is an anomaly.
    """
    try:
        try:
            model_name = event["model_name"]
            model_version = event["model_version"]
            value = event["value"]
            timestamp = event["timestamp"]
        except KeyError as e:
            print(f"Key {e} not found")

        if "body" in event:
            body = json.loads(event["body"])
            model_name = body.get("model_name")
            model_version = body.get("model_version")
            value = body.get("value")
            timestamp = body.get("timestamp")

        model = load_model(model_name=model_name, model_version=model_version)
        data_point = DataPoint(value=value, timestamp=timestamp)
        is_anomaly = model.predict(data_point)

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

        return {"statusCode": 200, "body": json.dumps({"is_anomaly": is_anomaly})}
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}

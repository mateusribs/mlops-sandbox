import json
import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import boto3
from aws_lambda_powertools.event_handler import APIGatewayRestResolver

app = APIGatewayRestResolver()
classifier_params = None
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

MODEL_REGISTRY_TABLE = os.environ.get("MODEL_REGISTRY_TABLE", "model-registry")


@dataclass
class DataPoint:
    value: float
    timestamp: str


class ToyLevelClassifier:
    def __init__(self, baseline_avg: float, std_dev: float):
        self.baseline_avg = baseline_avg
        self.std_dev = std_dev

    def predict(self, data_point: DataPoint) -> str:
        deviation = (data_point.value - self.baseline_avg) / self.std_dev

        if deviation > 1.5:
            return "high"
        elif deviation < -1.5:
            return "low"
        else:
            return "normal"


def get_model_metadata(model_name: str, model_version: str) -> dict:
    """Fetch model metadata from DynamoDB registry.

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


def load_model(model_name: str, model_version: str) -> ToyLevelClassifier:
    """Load the level classifier model from S3 based on metadata from DynamoDB.

    Args:
        model_name (str): The name of the model to load.
        model_version (str): The version of the model to load.

    Returns:
        ToyLevelClassifier: The loaded level classifier model.
    """
    global classifier_params

    if classifier_params is None:
        metadata = get_model_metadata(model_name, model_version)
        s3.download_file(metadata["s3_bucket"], metadata["s3_key"], "/tmp/model.json")

        with open("/tmp/model.json") as f:
            classifier_params = json.load(f)

        print(f"Loaded model {model_name}@{model_version} from {metadata['s3_key']}")

    return ToyLevelClassifier(
        baseline_avg=classifier_params["baseline_avg"], std_dev=classifier_params["std_dev"]
    )


@app.post("/level")
def classify_level():
    payload = app.current_event.json_body
    try:
        model_name = payload.get("model_name")
        model_version = payload.get("model_version")
        value = payload.get("value")
        timestamp = payload.get("timestamp")
    except KeyError as e:
        KeyError(f"Missing required field in payload: {e}")

    model = load_model(model_name=model_name, model_version=model_version)
    data_point = DataPoint(value=value, timestamp=timestamp)
    level = model.predict(data_point)

    predictions_table = dynamodb.Table("model-predictions")
    predictions_table.put_item(
        Item={
            "model_name": model_name,
            "timestamp": datetime.now().isoformat(),
            "version": model_version,
            "input": {"value": Decimal(str(value)), "timestamp": timestamp},
            "output": {"level": level},
        }
    )

    return {"level": level}


def handler(event, context):
    """AWS Lambda handler for classifying data point levels.

    Args:
        event (dict): The event payload containing the data point to classify.
        context (LambdaContext): The runtime information of the Lambda function.

    Returns:
        dict: The classification result (high/normal/low).
    """
    return app.resolve(event, context)

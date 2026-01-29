import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from src.models.toy_anomaly_classifier import ToyAnomalyClassifier
from src.schemas.data_point import DataPoint, TimeSeries
from src.utils.model_registry import register_model_version
from src.utils.s3 import upload_model_to_s3


def train(version: str = "v1") -> tuple[str, dict]:
    """
    Train anomaly classifier model.

    Args:
        version: Simple version
    """
    # Example usage
    data_points = [
        DataPoint(value=10.0, timestamp="1622548800"),
        DataPoint(value=12.0, timestamp="1622548860"),
        DataPoint(value=11.5, timestamp="1622548920"),
        DataPoint(value=13.0, timestamp="1622548980"),
        DataPoint(value=50.0, timestamp="1622549040"),  # Anomalous point
    ]
    time_series = TimeSeries(data_points=data_points)

    model = ToyAnomalyClassifier()
    model.fit(time_series)

    model_path = f"toy_anomaly_classifier_{version}.json"
    model.save_model(model_path)

    metrics = {
        "mean": model.mean,
        "std": model.std,
        "threshold": model.threshold,
    }

    return model_path, metrics


if __name__ == "__main__":
    load_dotenv()

    version = os.environ.get("ANOMALY_CLASSIFIER_MODEL_VERSION", "v1")

    bucket_name = "anomaly-classifier-models"
    model_path, metrics = train(version)

    # Upload to S3 with versioned key
    s3_key = f"models/{version}/toy_anomaly_classifier.json"
    upload_model_to_s3(model_path, bucket_name, s3_key)

    # Register in DynamoDB
    register_model_version(
        model_name="anomaly_classifier",
        version=version,
        s3_bucket=bucket_name,
        s3_key=s3_key,
        model_type="ToyAnomalyClassifier",
    )

    Path(model_path).unlink()
    logger.info(f"Model {version} trained, uploaded, and registered")

import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from src.models.toy_level_classifier import ToyLevelClassifier
from src.schemas.data_point import DataPoint, TimeSeries
from src.utils.model_registry import register_model_version
from src.utils.s3 import upload_model_to_s3


def train(version: str = "v1") -> tuple[str, dict]:
    """
    Train level classifier model.

    Args:
        version: Simple version (e.g., v1, v2, v3)
                 Increment for each new training run
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

    model = ToyLevelClassifier()
    model.fit(time_series)

    model_path = f"toy_level_classifier_{version}.json"
    model.save_model(model_path)

    metrics = {"baseline_avg": float(model.baseline_avg), "std_dev": float(model.std_dev)}

    return model_path, metrics


if __name__ == "__main__":
    load_dotenv()

    version = os.environ.get("LEVEL_CLASSIFIER_MODEL_VERSION", "v1")

    bucket_name = "level-classifier-models"
    model_path, metrics = train(version)

    # Upload to S3 with versioned key
    s3_key = f"models/{version}/toy_level_classifier.json"
    upload_model_to_s3(model_path, bucket_name, s3_key)

    # Register in DynamoDB
    register_model_version(
        model_name="level_classifier",
        version=version,
        s3_bucket=bucket_name,
        s3_key=s3_key,
        model_type="ToyLevelClassifier",
        metrics=metrics,
    )

    Path(model_path).unlink()
    logger.info(f"Model {version} trained, uploaded, and registered")

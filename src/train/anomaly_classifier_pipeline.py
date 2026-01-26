import logging
from pathlib import Path

from dotenv import load_dotenv

from src.models.toy_anomaly_classifier import ToyAnomalyClassifier
from src.schemas.data_point import DataPoint, TimeSeries
from src.utils.s3 import upload_model_to_s3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def train() -> str:
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

    model_path = "toy_anomaly_classifier.pkl"
    model.save_model(model_path)
    return model_path


if __name__ == "__main__":
    load_dotenv()
    model_path = train()
    bucket_name = "anomaly-classifier-models"
    upload_model_to_s3(model_path, bucket_name, model_path)
    Path(model_path).unlink()  # Clean up local file after upload

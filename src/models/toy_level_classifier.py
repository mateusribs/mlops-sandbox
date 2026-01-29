import json
from datetime import datetime

from src.schemas.data_point import DataPoint, TimeSeries


class ToyLevelClassifier:
    def __init__(self) -> None:
        self.baseline_avg = None
        self.std_dev = None

    def fit(self, data: TimeSeries) -> None:
        """Fits the model to the provided time series data.

        Args:
            data (TimeSeries): The time series data to fit the model on.
        """
        values_stream = [d.value for d in data.data_points]
        self.baseline_avg = sum(values_stream) / len(values_stream)
        variance = sum((x - self.baseline_avg) ** 2 for x in values_stream) / len(values_stream)
        self.std_dev = variance**0.5

    def predict(self, data_point: DataPoint) -> str:
        """Classifies the given data point as high, normal, or low.

        Args:
            data_point (DataPoint): The data point to classify.

        Returns:
            str: "high", "normal", or "low"
        """
        deviation = (data_point.value - self.baseline_avg) / self.std_dev

        if deviation > 1.5:
            return "high"
        elif deviation < -1.5:
            return "low"
        else:
            return "normal"

    def to_dict(self) -> dict:
        """Serializes model parameters to dictionary.

        Returns:
            dict: Model parameters including version metadata.
        """
        return {
            "baseline_avg": self.baseline_avg,
            "std_dev": self.std_dev,
            "model_type": "ToyLevelClassifier",
            "version": datetime.now().isoformat(),
        }

    def save_model(self, file_path: str) -> None:
        """Saves the model parameters to a JSON file.

        Args:
            file_path (str): The path to the file where the model will be saved.
        """
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f)

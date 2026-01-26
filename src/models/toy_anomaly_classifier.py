import pickle

import numpy as np

from src.schemas.data_point import DataPoint, TimeSeries


class ToyAnomalyClassifier:
    def __init__(self) -> None:
        self.mean = None
        self.std = None
        self.threshold = None

    def fit(self, data: TimeSeries) -> None:
        """Fits the model to the provided time series data.

        Args:
            data (TimeSeries): The time series data to fit the model on.
        """
        values_stream = [d.value for d in data.data_points]
        self.mean = np.mean(values_stream)
        self.std = np.std(values_stream)
        self.threshold = self.mean + 3 * self.std

    def predict(self, data_point: DataPoint) -> bool:
        """Predicts whether the given data point is an anomaly.

        Args:
            data_point (DataPoint): The data point to evaluate.

        Returns:
            bool: True if the data point is an anomaly, False otherwise.
        """
        return data_point.value > self.threshold

    def save_model(self, file_path: str) -> None:
        """Saves the model parameters to a file.

        Args:
            file_path (str): The path to the file where the model will be saved.
        """
        with open(file_path, "wb") as f:
            pickle.dump(self, f)

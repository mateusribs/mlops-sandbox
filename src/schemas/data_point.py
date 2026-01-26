from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class DataPoint:
    value: float
    timestamp: str


@dataclass
class TimeSeries:
    data_points: Sequence[DataPoint]

from abc import ABC, abstractmethod

import pandas as pd


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str):
        self.name = name

    def validate_data(self, data: pd.DataFrame, min_rows: int) -> bool:
        """Standard guard for data integrity."""
        if data is None or data.empty:
            return False
        if len(data) < min_rows:
            return False
        # Check if the most recent price is NaN (dangerous for signals)
        if pd.isna(data["close"].iloc[-1]):
            return False
        return True

    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> str:
        pass

from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Analyze data and return a signal: 'buy', 'sell', or 'hold'.
        """
        pass

from abc import ABC, abstractmethod
import pandas as pd

class BaseConnector(ABC):
    """Abstract base class for exchange connectors."""
    
    def __init__(self, exchange_id: str, api_key: str = None, secret: str = None):
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.secret = secret
        self.client = self._init_client()

    @abstractmethod
    def _init_client(self):
        """Initialize the exchange client (e.g., CCXT client)."""
        pass

    @abstractmethod
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Fetch historical OHLCV data."""
        pass

    @abstractmethod
    def create_order(self, symbol: str, order_type: str, side: str, amount: float, price: float = None):
        """Create a new order."""
        pass

    @abstractmethod
    def get_balance(self) -> dict:
        """Retrieve account balance."""
        pass

import ccxt
import pandas as pd
from .base import BaseConnector

class BinanceConnector(BaseConnector):
    """Implementation of Binance connector using CCXT."""
    
    def _init_client(self):
        return ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.secret,
            'enableRateLimit': True,
        })

    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Fetch historical OHLCV data from Binance."""
        raw_data = self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(raw_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def create_order(self, symbol: str, order_type: str, side: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Create a new order on Binance."""
        if order_type.lower() == 'market':
            return self.client.create_market_order(symbol, side, amount)
        elif order_type.lower() == 'limit':
            return self.client.create_limit_order(symbol, side, amount, price)
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

    def get_balance(self) -> Dict[str, Any]:
        """Fetch full account balance."""
        return self.client.fetch_balance()

    def fetch_balance(self, asset: str) -> float:
        """Fetch free balance for a specific asset (e.g. 'USDT')."""
        balances = self.get_balance()
        return float(balances.get('free', {}).get(asset, 0.0))

    def create_safety_order(self, symbol: str, side: str, amount: float, stop_price: float, price: float = None):
        """Create a Stop-Loss or Take-Profit order on the exchange."""
        # side should be opposite of position (if long, side is 'sell')
        params = {
            'stopPrice': stop_price,
        }
        return self.client.create_order(symbol, 'limit', side, amount, price, params)

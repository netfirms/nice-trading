import pandas as pd

from engine.indicators import bollinger_bands, rsi
from engine.strategy_manager import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """Mean Reversion strategy using Bollinger Bands and RSI."""

    def __init__(self, bb_window: int = 20, bb_std: float = 2.0, rsi_window: int = 14):
        super().__init__("Mean Reversion (BB + RSI)")
        self.bb_window = bb_window
        self.bb_std = bb_std
        self.rsi_window = rsi_window

    def generate_signal(self, data: pd.DataFrame) -> str:
        if not self.validate_data(data, self.bb_window + 1):
            return "hold"

        # Indicators
        upper, mid, lower = bollinger_bands(
            data["close"], window=self.bb_window, num_std=self.bb_std
        )
        rsi_vals = rsi(data["close"], window=self.rsi_window)

        curr_price = data["close"].iloc[-1]
        curr_rsi = rsi_vals.iloc[-1]
        curr_lower = lower.iloc[-1]
        curr_upper = upper.iloc[-1]

        # BUY: Price below lower band AND RSI oversold
        if curr_price < curr_lower and curr_rsi < 30:
            return "buy"

        # SELL: Price above upper band AND RSI overbought (or just hitting target)
        if curr_price > curr_upper and curr_rsi > 70:
            return "sell"

        return "hold"

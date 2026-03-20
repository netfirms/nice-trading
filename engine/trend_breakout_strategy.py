import pandas as pd

from engine.indicators import donchian_channels
from engine.strategy_manager import BaseStrategy


class TrendBreakoutStrategy(BaseStrategy):
    """Trend Follower strategy using Donchian Channel breakouts."""

    def __init__(self, window: int = 20):
        super().__init__("Trend Breakout (Donchian)")
        self.window = window

    def generate_signal(self, data: pd.DataFrame) -> str:
        if not self.validate_data(data, self.window + 1):
            return "hold"

        # Indicators
        upper, mid, lower = donchian_channels(data["high"], data["low"], window=self.window)

        curr_price = data["close"].iloc[-1]
        # We look at the channel value from the PREVIOUS candle to define the breakout bound
        prev_upper = upper.iloc[-2]
        prev_lower = lower.iloc[-2]

        # BUY: Close breaks above previous N-period high
        if curr_price > prev_upper:
            return "buy"

        # SELL: Close breaks below previous N-period low (or stop loss)
        if curr_price < prev_lower:
            return "sell"

        return "hold"

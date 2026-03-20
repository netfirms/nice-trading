import pandas as pd

from engine.indicators import macd, rsi
from engine.strategy_manager import BaseStrategy


class AdvancedStrategy(BaseStrategy):
    """Strategy combining SMA crossover with RSI and MACD."""

    def __init__(self, fast_sma: int = 10, slow_sma: int = 30, rsi_window: int = 14):
        super().__init__("Advanced Multi-Indicator")
        self.fast_sma = fast_sma
        self.slow_sma = slow_sma
        self.rsi_window = rsi_window

    def generate_signal(self, data: pd.DataFrame) -> str:
        if not self.validate_data(data, self.slow_sma + 1):
            return "hold"

        # Indicators
        data["sma_fast"] = data["close"].rolling(window=self.fast_sma).mean()
        data["sma_slow"] = data["close"].rolling(window=self.slow_sma).mean()
        data["rsi"] = rsi(data["close"], window=self.rsi_window)
        macd_line, signal_line, _ = macd(data["close"])

        curr = data.iloc[-1]
        prev = data.iloc[-2]

        # Logic:
        # Buy if: SMA Fast crosses up SMA Slow AND RSI < 70 (not overbought)
        # Sell if: SMA Fast crosses down SMA Slow OR RSI > 70 (overbought)

        if prev["sma_fast"] <= prev["sma_slow"] and curr["sma_fast"] > curr["sma_slow"]:
            if curr["rsi"] < 70:
                return "buy"

        if (prev["sma_fast"] >= prev["sma_slow"] and curr["sma_fast"] < curr["sma_slow"]) or curr[
            "rsi"
        ] > 80:
            return "sell"

        return "hold"

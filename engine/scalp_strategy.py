import pandas as pd

from engine.indicators import ema, rsi
from engine.strategy_manager import BaseStrategy


class ScalpStrategy(BaseStrategy):
    """High-frequency Scalp strategy targeting small, rapid profits."""

    def __init__(
        self,
        fast_ema: int = 9,
        slow_ema: int = 21,
        rsi_window: int = 4,
        target_profit: float = 0.005,
    ):
        super().__init__("Momentum Scalper")
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.rsi_window = rsi_window
        self.target_profit = target_profit
        self.entry_price = None

    def generate_signal(self, data: pd.DataFrame) -> str:
        if not self.validate_data(data, self.slow_ema + 1):
            return "hold"

        # Indicators
        data["ema_fast"] = ema(data["close"], window=self.fast_ema)
        data["ema_slow"] = ema(data["close"], window=self.slow_ema)
        data["rsi_scalp"] = rsi(data["close"], window=self.rsi_window)

        curr = data.iloc[-1]

        # BUY: Strong short-term momentum upward + extreme local dip
        if curr["ema_fast"] > curr["ema_slow"] and curr["rsi_scalp"] < 20:
            if self.entry_price is None:  # Only if not already in a scalp
                self.entry_price = curr["close"]
                return "buy"

        # SELL: Exit on target profit, or trend reversal, or extreme overbought
        if self.entry_price:
            profit = (curr["close"] - self.entry_price) / self.entry_price
            if profit >= self.target_profit:
                self.entry_price = None
                return "sell"

            if curr["ema_fast"] < curr["ema_slow"] or curr["rsi_scalp"] > 80:
                self.entry_price = None
                return "sell"

        return "hold"

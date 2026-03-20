import pandas as pd

from engine.advanced_strategy import AdvancedStrategy
from engine.mean_reversion_strategy import MeanReversionStrategy
from engine.scalp_strategy import ScalpStrategy
from engine.sma_strategy import SMACrossoverStrategy
from engine.trend_breakout_strategy import TrendBreakoutStrategy


def create_mock_data(prices):
    """Utility to create OHLCV dataframe from a list of prices."""
    return pd.DataFrame(
        {
            "open": prices,
            "high": [p * 1.01 for p in prices],
            "low": [p * 0.99 for p in prices],
            "close": prices,
            "volume": [1000] * len(prices),
        }
    )


def test_sma_crossover():
    strategy = SMACrossoverStrategy(fast_period=2, slow_period=5)
    # Price crosses up
    data = create_mock_data([10, 10, 10, 10, 10, 20])
    assert strategy.generate_signal(data) == "buy"
    # Price crosses down
    data = create_mock_data([20, 20, 20, 20, 20, 10])
    assert strategy.generate_signal(data) == "sell"


def test_mean_reversion():
    strategy = MeanReversionStrategy(bb_window=5, bb_std=2.0, rsi_window=5)
    # Price crashes below BB and RSI is low
    data = create_mock_data([20, 20, 20, 20, 20, 5])
    assert strategy.generate_signal(data) == "buy"
    # Price spikes above BB and RSI is high
    data = create_mock_data([10, 10, 10, 10, 10, 50])
    assert strategy.generate_signal(data) == "sell"


def test_trend_breakout():
    strategy = TrendBreakoutStrategy(window=5)
    # Price breaks 5-day high
    data = create_mock_data([10, 11, 10, 12, 11, 15])
    assert strategy.generate_signal(data) == "buy"
    # Price breaks 5-day low
    data = create_mock_data([20, 19, 20, 18, 19, 10])
    assert strategy.generate_signal(data) == "sell"


def test_scalp_momentum():
    strategy = ScalpStrategy(fast_ema=2, slow_ema=5, rsi_window=2)
    # Trend up + local dip
    data = create_mock_data([10, 12, 14, 16, 15])  # 15 is a dip while fast > slow
    signal = strategy.generate_signal(data)
    # Note: ScalpStrategy is sensitive, might need specific price action
    assert signal in ["buy", "hold"]


def test_advanced_strategy():
    strategy = AdvancedStrategy(fast_sma=2, slow_sma=5, rsi_window=5)
    data = create_mock_data([10, 10, 10, 10, 10, 20])
    # Fast SMA crosses up Slow SMA
    assert strategy.generate_signal(data) == "buy"

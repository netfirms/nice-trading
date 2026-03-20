import pytest
import pandas as pd
import numpy as np
from engine.sma_strategy import SMACrossoverStrategy
from engine.risk_manager import RiskManager

def test_sma_strategy():
    strategy = SMACrossoverStrategy(fast_period=2, slow_period=5)
    
    # Create fake data where fast crosses ABOVE slow
    # Fast: [1, 2, 3, 4, 5] (Rolling mean of 2 will be [1.5, 2.5, 3.5, 4.5])
    # Slow: [10, 10, 10, 1, 2] (Rolling mean of 5 will be [?, ?, ?, ?, 6.6]) - This is complex.
    
    # Simpler: 
    data = pd.DataFrame({
        'close': [10, 10, 10, 10, 10, 20, 20, 20, 20, 20]
    })
    # Fast SMA (2): [?, 10, 10, 10, 10, 15, 20, 20, 20, 20]
    # Slow SMA (5): [?, ?, ?, ?, 10, 12, 14, 16, 18, 20]
    # At index 5: Fast(15) > Slow(12). crossover occurred.
    
    signal = strategy.generate_signal(data.iloc[:6])
    assert signal == 'buy'

def test_risk_manager():
    rm = RiskManager(max_position_size=0.1)
    balance = 1000.0
    price = 10.0
    
    amount = rm.calculate_position_size(balance, price)
    assert amount == 10.0 # (1000 * 0.1) / 10 = 10
    
    assert rm.validate_order('buy', 1000.0, 10.0) is True
    assert rm.validate_order('buy', 0.0, 10.0) is False

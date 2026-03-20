import pandas as pd
from .strategy_manager import BaseStrategy

class SMACrossoverStrategy(BaseStrategy):
    """Simple Moving Average Crossover strategy."""
    
    def __init__(self, fast_period: int = 10, slow_period: int = 50):
        super().__init__("SMA Crossover")
        self.fast_period = fast_period
        self.slow_period = slow_period

    def generate_signal(self, data: pd.DataFrame) -> str:
        if len(data) < self.slow_period:
            return 'hold'
            
        # Calculate moving averages
        fast_ama = data['close'].rolling(window=self.fast_period).mean()
        slow_ama = data['close'].rolling(window=self.slow_period).mean()
        
        # Get the two most recent values
        current_fast = fast_ama.iloc[-1]
        current_slow = slow_ama.iloc[-1]
        prev_fast = fast_ama.iloc[-2]
        prev_slow = slow_ama.iloc[-2]
        
        # Signal logic: Crossover
        if prev_fast <= prev_slow and current_fast > current_slow:
            return 'buy'
        elif prev_fast >= prev_slow and current_fast < current_slow:
            return 'sell'
            
        return 'hold'

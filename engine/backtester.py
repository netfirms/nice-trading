import pandas as pd
from typing import List, Dict

class BacktestEngine:
    """Simulates trading strategy on historical data."""
    
    def __init__(self, initial_balance: float = 1000.0, commission: float = 0.001):
        self.initial_balance = initial_balance
        self.commission = commission
        self.balance = initial_balance
        self.position = 0.0 # Asset amount
        self.trades: List[Dict] = []

    def run(self, strategy, data: pd.DataFrame) -> Dict:
        """
        Runs the strategy on the provided historical OHLCV data.
        Assumes 'data' is a DataFrame with 'timestamp', 'open', 'high', 'low', 'close', 'volume'.
        """
        print(f"Starting backtest for {strategy.name}...")
        
        for i in range(len(data)):
            # Strategy only sees data UP TO the current index
            current_data = data.iloc[:i+1]
            if len(current_data) < 2:
                continue
                
            signal = strategy.generate_signal(current_data)
            current_price = data.iloc[i]['close']
            timestamp = data.iloc[i]['timestamp']
            
            if signal == 'buy' and self.balance > 0:
                # Buy with all available balance
                cost = self.balance * (1 - self.commission)
                self.position = cost / current_price
                self.balance = 0
                self.trades.append({
                    'type': 'buy',
                    'price': current_price,
                    'timestamp': timestamp,
                    'balance': self.balance + (self.position * current_price)
                })
                
            elif signal == 'sell' and self.position > 0:
                # Sell all positions
                proceeds = self.position * current_price * (1 - self.commission)
                self.balance = proceeds
                self.position = 0
                self.trades.append({
                    'type': 'sell',
                    'price': current_price,
                    'timestamp': timestamp,
                    'balance': self.balance
                })

        # Calculate results
        final_value = self.balance + (self.position * data.iloc[-1]['close'])
        total_return = (final_value - self.initial_balance) / self.initial_balance
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': final_value,
            'total_return_pct': total_return * 100,
            'number_of_trades': len(self.trades),
            'trades': self.trades
        }

    def optimize_params(self, strategy_class, data: pd.DataFrame, param_grid: Dict[str, List]) -> Dict:
        """
        Finds the best parameters for a strategy by iterating through a grid.
        param_grid: {'slow': [20, 30, 40], 'fast': [10, 15]}
        """
        import itertools
        
        best_return = -float('inf')
        best_params = None
        results = []

        # Generate all combinations of parameters
        keys, values = zip(*param_grid.items())
        for v in itertools.product(*values):
            params = dict(zip(keys, v))
            
            # Reset engine for each run
            self.balance = self.initial_balance
            self.position = 0.0
            self.trades = []
            
            # Instantiate strategy with params
            strategy = strategy_class(**params)
            res = self.run(strategy, data)
            
            results.append({
                'params': params,
                'total_return_pct': res['total_return_pct']
            })
            
            if res['total_return_pct'] > best_return:
                best_return = res['total_return_pct']
                best_params = params

        return {
            'best_params': best_params,
            'best_total_return_pct': best_return,
            'all_results': sorted(results, key=lambda x: x['total_return_pct'], reverse=True)
        }

    def print_summary(self, results: Dict):
        print("\n--- Backtest Summary ---")
        print(f"Initial Balance: {results['initial_balance']:.2f}")
        print(f"Final Balance:   {results['final_balance']:.2f}")
        print(f"Total Return:    {results['total_return_pct']:.2f}%")
        print(f"Total Trades:    {results['number_of_trades']}")
        print("------------------------\n")

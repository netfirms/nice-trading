import os
from dotenv import load_dotenv
from connectors.binance_connector import BinanceConnector
from engine.sma_strategy import SMACrossoverStrategy
from engine.backtester import BacktestEngine

load_dotenv()

def main():
    print("Nice Trading Robot - Backtester")
    
    # 1. Setup Data Source
    symbol = os.getenv('SYMBOL', 'BTC/USDT')
    timeframe = os.getenv('TIMEFRAME', '1h')
    connector = BinanceConnector('binance')
    
    print(f"Fetching historical data for {symbol}...")
    # Fetch 500 candles for a decent backtest
    data = connector.get_ohlcv(symbol, timeframe, limit=500)
    
    # 2. Setup Strategy and Backtester
    strategy = SMACrossoverStrategy(fast_period=10, slow_period=30)
    backtester = BacktestEngine(initial_balance=1000.0)
    
    # 3. Run Backtest
    results = backtester.run(strategy, data)
    
    # 4. Print Results
    backtester.print_summary(results)
    
    if len(results['trades']) > 0:
        print("Last 5 trades:")
        for trade in results['trades'][-5:]:
            print(f"  {trade['timestamp']} | {trade['type'].upper()} at {trade['price']:.2f} | Portfolio: {trade['balance']:.2f}")

if __name__ == "__main__":
    main()

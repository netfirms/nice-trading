import time
import os
import signal
import sys
from multiprocessing import Process, Event
from storage.db import Storage
from utils.logger import setup_logger
from utils.decorators import retry_on_failure

# Import these to make sure they are available in the subprocess
from connectors.binance_connector import BinanceConnector
from engine.strategy_manager import StrategyManager
from engine.risk_manager import RiskManager
from storage.cache import Cache

class BotRunner:
    def __init__(self, bot_id, symbol, strategy_name, params=None):
        self.bot_id = bot_id
        self.symbol = symbol
        self.strategy_name = strategy_name
        self.params = params or {}
        self.logger = setup_logger(f"bot_{symbol.replace('/', '_')}", f"logs/bot_{symbol.replace('/', '_')}.log")
        self.stop_event = Event()

    def run(self):
        self.logger.info(f"🚀 Starting Bot Runner for {self.symbol} with {self.strategy_name}")
        
        try:
            connector = BinanceConnector(
                'binance', 
                os.getenv("BINANCE_API_KEY"), 
                os.getenv("BINANCE_SECRET")
            )
            storage = Storage()
            cache = Cache()
            risk_manager = RiskManager()
            
            # 0. Sync state with exchange (e.g. check open orders)
            self.sync_exchange_state(connector)
            
            # Load strategy
            from engine.sma_strategy import SMACrossoverStrategy
            from engine.advanced_strategy import AdvancedStrategy
            
            if self.strategy_name == 'advanced':
                strategy = AdvancedStrategy()
            else:
                strategy = SMACrossoverStrategy()

            while not self.stop_event.is_set():
                try:
                    # 1. Fetch data
                    ohlcv = connector.fetch_ohlcv(self.symbol)
                    current_price = float(cache.get_last_price(self.symbol) or ohlcv['close'].iloc[-1])
                    
                    # 2. Generate signal
                    signal = strategy.generate_signal(ohlcv)
                    
                    # 3. Execute Signal
                    if signal != 'hold':
                        self.logger.info(f"Signal: {signal} for {self.symbol} at {current_price}")
                        
                        # 1a. Fetch Live Balance (Phase 27)
                        quote_asset = self.symbol.split('/')[1]
                        balance = connector.fetch_balance(quote_asset)
                        
                        # Validate with Risk Manager
                        is_safe, amount, message = risk_manager.validate_order(signal, balance, current_price)
                        
                        if is_safe:
                            # In a real bot, we would call connector.execute_order
                            self.logger.info(f"DRY RUN: Executing {signal} for {amount} {self.symbol} (Balance: {balance})")
                            
                            # Place Exchange-Side Safety Orders (Phase 28)
                            if signal == 'buy':
                                sl_price = current_price * (1 - risk_manager.stop_loss_pct)
                                tp_price = current_price * (1 + (risk_manager.stop_loss_pct * 2)) # Simple 2:1 RR
                                self.logger.info(f"Setting Exchange-Side SL at {sl_price} and TP at {tp_price}")
                                # connector.create_safety_order(self.symbol, 'sell', amount, sl_price)
                            
                            storage.save_trade(self.symbol, signal, amount, current_price, pnl=0)
                        else:
                            self.logger.warning(f"Risk Warning: {message}")

                    time.sleep(10) # Bot loop frequency
                except Exception as e:
                    self.logger.error(f"Error in bot loop: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            self.logger.critical(f"Bot Runner failed to initialize: {e}")

    @retry_on_failure(retries=3, delay=2)
    def fetch_data(self, connector):
        return connector.fetch_ohlcv(self.symbol)

    def sync_exchange_state(self, connector):
        """Check for orphaned open orders on start."""
        self.logger.info("Synchronizing state with exchange...")
        try:
            # In a real bot, we would fetch open orders and decide to cancel or track them
            # open_orders = connector.fetch_open_orders(self.symbol)
            # self.logger.info(f"Found {len(open_orders)} open orders")
            pass
        except Exception as e:
            self.logger.error(f"Failed to sync state: {e}")

def start_bot_process(bot_id, symbol, strategy_name, params):
    runner = BotRunner(bot_id, symbol, strategy_name, params)
    runner.run()

import os
import time
import signal
import sys
from utils.config_handler import load_config
from utils.logger import setup_logger
from connectors.binance_connector import BinanceConnector
from engine.advanced_strategy import AdvancedStrategy
from engine.sma_strategy import SMACrossoverStrategy
from engine.risk_manager import RiskManager
from storage.db import Storage

# Setup Logging
logger = setup_logger()

# Global status for graceful shutdown
running = True

def signal_handler(sig, frame):
    global running
    logger.info("Shutdown signal received. Finishing current loop...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_strategy(name: str, config: dict):
    if name == 'advanced':
        st_cfg = config['strategy']
        return AdvancedStrategy(
            fast_sma=st_cfg['fast_sma'], 
            slow_sma=st_cfg['slow_sma'], 
            rsi_window=st_cfg['rsi_window']
        )
    elif name == 'sma':
        return SMACrossoverStrategy()
    else:
        logger.error(f"Unknown strategy: {name}. Falling back to SMA.")
        return SMACrossoverStrategy()

def main():
    logger.info("Nice Trading Robot Starting...")
    
    try:
        # Load initial configuration
        config = load_config()
        ex_cfg = config['exchange']
        rs_cfg = config['risk']
        
        # Initialize components
        connector = BinanceConnector(ex_cfg['id'], ex_cfg['api_key'], ex_cfg['secret'])
        risk_manager = RiskManager(
            max_position_size=rs_cfg['max_position_size'],
            stop_loss_pct=rs_cfg['stop_loss_pct']
        )
        storage = Storage()
        
        # Initial strategy
        current_strategy_name = 'advanced'
        strategy = get_strategy(current_strategy_name, config)
        
        logger.info(f"Symbol: {ex_cfg['symbol']} | Dry Run: {ex_cfg['dry_run']}")
        
        while running:
            try:
                # 0. Check Shared State (Database)
                state = storage.get_bot_state()
                
                # Handle Pause/Stop
                if not state.is_running:
                    logger.debug("Bot is paused. Waiting...")
                    time.sleep(10)
                    continue
                
                # Handle Dynamic Strategy Change
                if state.current_strategy != current_strategy_name:
                    logger.info(f"Switching strategy from {current_strategy_name} to {state.current_strategy}")
                    current_strategy_name = state.current_strategy
                    strategy = get_strategy(current_strategy_name, config)
                
                # 1. Fetch Market Data
                ohlcv = connector.get_ohlcv(ex_cfg['symbol'], ex_cfg['timeframe'], limit=100)
                current_price = ohlcv['close'].iloc[-1]
                
                # 2. Generate Signal
                signal_type = strategy.generate_signal(ohlcv)
                logger.debug(f"Current Price: {current_price} | Signal: {signal_type}")
                
                # 3. Handle Signal with Risk Management
                if signal_type != 'hold':
                    # Determine balance for risk calculation
                    if not ex_cfg['dry_run'] and ex_cfg['api_key']:
                        balance_info = connector.get_balance()
                        quote_currency = ex_cfg['symbol'].split('/')[1]
                        balance = balance_info['total'].get(quote_currency, 0)
                    else:
                        balance = 1000.0 if signal_type == 'buy' else 0.1 
                    
                    if risk_manager.validate_order(signal_type, balance, current_price):
                        amount = risk_manager.calculate_position_size(balance, current_price)
                        
                        if ex_cfg['dry_run']:
                            logger.info(f"[DRY RUN] {signal_type.upper()} {amount:.6f} {ex_cfg['symbol']} at {current_price}")
                            storage.save_trade(ex_cfg['symbol'], signal_type, amount, current_price, pnl=0.0)
                        else:
                            logger.info(f"Executing {signal_type.upper()} {amount:.6f} {ex_cfg['symbol']}...")
                            order = connector.create_order(ex_cfg['symbol'], 'market', signal_type, amount)
                            logger.info(f"Order Success ID: {order['id']}")
                            storage.save_trade(ex_cfg['symbol'], signal_type, amount, current_price)
                    else:
                        logger.warning("Order blocked by Risk Manager.")
                
                # 4. Wait for next interval
                time.sleep(60) 
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(10)
                
    except Exception as e:
        logger.critical(f"Fatal Startup Error: {e}")
        sys.exit(1)
        
    logger.info("Nice Trading Robot Shutdown Cleanly.")

if __name__ == "__main__":
    main()

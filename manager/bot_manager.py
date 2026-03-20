import time
import os
import signal
from multiprocessing import Process
from storage.db import Storage
from utils.logger import setup_logger
from manager.bot_runner import start_bot_process

logger = setup_logger("bot_manager", "logs/manager.log")

class BotManager:
    def __init__(self):
        self.storage = Storage()
        self.processes = {} # {symbol: Process}
        self.running = True

    def sync_bots(self):
        """Synchronize running processes with database configuration."""
        active_configs = self.storage.get_bot_configs(active_only=True)
        active_symbols = [c.symbol for c in active_configs]
        
        # 1. Stop processes that are no longer active in DB
        for symbol in list(self.processes.keys()):
            if symbol not in active_symbols:
                logger.info(f"Stopping bot for {symbol}")
                self.processes[symbol].terminate()
                self.processes[symbol].join()
                del self.processes[symbol]

        # 2. Start processes for new active configs
        for config in active_configs:
            if config.symbol not in self.processes:
                logger.info(f"Starting bot for {config.symbol}")
                p = Process(
                    target=start_bot_process, 
                    args=(config.id, config.symbol, config.strategy, config.params)
                )
                p.start()
                self.processes[config.symbol] = p

    def run(self):
        logger.info("Bot Manager started. Watching for active configurations...")
        
        while self.running:
            try:
                self.sync_bots()
                time.sleep(5) # Sync every 5 seconds
            except Exception as e:
                logger.error(f"Error in Bot Manager sync: {e}")
                time.sleep(10)

    def stop_all(self):
        logger.info("Stopping all bots...")
        for symbol, p in self.processes.items():
            p.terminate()
            p.join()
        self.running = False

def main():
    manager = BotManager()
    
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        manager.stop_all()
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager.run()

if __name__ == "__main__":
    main()

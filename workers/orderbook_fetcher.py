import os
import sys
import time

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.binance_connector import BinanceConnector
from storage.cache import Cache
from storage.db import Storage
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("orderbook_worker", "logs/orderbook.log")


def main():
    symbol = os.getenv("SYMBOL", "BTC/USDT")
    logger.info(f"Starting Orderbook Fetcher for {symbol}...")

    connector = BinanceConnector(
        "binance", os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_SECRET")
    )
    cache = Cache()  # Uses settings.DATABASE_URL
    storage = Storage()  # Uses settings.DATABASE_URL

    while True:
        try:
            # Fetch L2 Orderbook
            orderbook = connector.exchange.fetch_order_book(symbol)
            best_bid = orderbook["bids"][0][0]
            best_ask = orderbook["asks"][0][0]

            # 1. Save to Redis (Real-time tracking)
            cache.set_orderbook(symbol, orderbook["bids"], orderbook["asks"])
            cache.set_last_price(symbol, best_bid)

            # 2. Save to QuestDB (Time-series history)
            storage.save_tick_questdb(symbol, best_bid, orderbook["bids"][0][1], "buy")
            storage.save_tick_questdb(symbol, best_ask, orderbook["asks"][0][1], "sell")

            logger.debug(f"Updated {symbol} Orderbook in Redis & QuestDB")

            # High frequency pull (e.g. every 500ms)
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Orderbook Fetcher Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()

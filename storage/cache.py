import redis
import json

class Cache:
    def __init__(self, host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def set_orderbook(self, symbol, bids, asks):
        """
        Saves L2 orderbook data to Redis.
        bids: list of [price, amount]
        asks: list of [price, amount]
        """
        # Store as JSON for simplicity in this MVP, 
        # but in HFT we would use Sorted Sets (ZADD).
        data = {
            'bids': bids[:10], # Keep top 10 for latency/size
            'asks': asks[:10]
        }
        self.client.set(f"orderbook:{symbol}", json.dumps(data))

    def get_orderbook(self, symbol):
        """Retrieves the latest orderbook from Redis."""
        data = self.client.get(f"orderbook:{symbol}")
        return json.loads(data) if data else None

    def set_last_price(self, symbol, price):
        self.client.set(f"price:{symbol}", price)

    def get_last_price(self, symbol):
        return self.client.get(f"price:{symbol}")

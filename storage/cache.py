import json

from psycopg2 import pool

from utils.config_handler import settings


class Cache:
    """High-speed cache using PostgreSQL 17 UNLOGGED tables (Redis replacement).
    Uses a connection pool to achieve Redis-like latency for HFT operations.
    """

    _pool = None

    def __init__(self, db_url: str = None):
        self.db_url = db_url or settings.DATABASE_URL
        self.degraded = False

        if not self.db_url:
            print("⚠️ DATABASE_URL not set. Running in DEGRADED mode (No Cache).")
            self.degraded = True
            return

        try:
            # Initialize singleton pool for the process
            if Cache._pool is None:
                Cache._pool = pool.ThreadedConnectionPool(1, 20, self.db_url)
            self._init_db()
        except Exception as e:
            print(f"⚠️ Failed to connect to PostgreSQL: {e}. Running in DEGRADED mode.")
            self.degraded = True

    def _init_db(self):
        if self.degraded or not self._pool:
            return
        conn = self._pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE UNLOGGED TABLE IF NOT EXISTS realtime_cache (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_cache_key ON realtime_cache (key);
                """
                )
            conn.commit()
        finally:
            self._pool.putconn(conn)

    def set_orderbook(self, symbol, bids, asks):
        data = json.dumps({"bids": bids[:10], "asks": asks[:10]})
        self._upsert(f"orderbook:{symbol}", data)

    def get_orderbook(self, symbol):
        val = self._get(f"orderbook:{symbol}")
        return json.loads(val) if val else None

    def set_last_price(self, symbol, price):
        self._upsert(f"price:{symbol}", str(price))

    def get_last_price(self, symbol):
        return self._get(f"price:{symbol}")

    def _upsert(self, key, value):
        if self.degraded or not self._pool:
            return
        conn = self._pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO realtime_cache (key, value, updated_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) DO UPDATE SET
                        value = EXCLUDED.value,
                        updated_at = EXCLUDED.updated_at;
                    NOTIFY realtime_update, %s;
                """,
                    (key, value, key),
                )
            conn.commit()
        finally:
            self._pool.putconn(conn)

    def _get(self, key):
        if self.degraded or not self._pool:
            return None
        conn = self._pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT value FROM realtime_cache WHERE key = %s", (key,))
                res = cur.fetchone()
                return res[0] if res else None
        finally:
            self._pool.putconn(conn)

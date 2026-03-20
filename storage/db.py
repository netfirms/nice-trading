from datetime import datetime
from typing import Optional

from questdb.ingress import IngressError, Sender
from sqlalchemy import Column, DateTime, FetchedValue, Float, Integer, String, create_engine, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.config_handler import settings

Base = declarative_base()


class Trade(Base):
    __tablename__ = "trades"
    # Use native UUIDv7 for timestamp-ordered primary keys (PG 18 Feature)
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=FetchedValue())
    symbol = Column(String)
    side = Column(String)  # 'buy' or 'sell'
    amount = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pnl = Column(Float, nullable=True)


class OHLCV(Base):
    __tablename__ = "ohlcv"
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    timestamp = Column(DateTime)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


class BotState(Base):
    __tablename__ = "bot_state"
    id = Column(Integer, primary_key=True)
    is_running = Column(Integer, default=1)  # 1=Running, 0=Stopped/Paused
    current_strategy = Column(String, default="advanced")
    symbol = Column(String, default="BTC/USDT")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BotConfig(Base):
    __tablename__ = "bot_configs"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    strategy = Column(String, default="sma")
    params = Column(String, default="{}")  # JSON string
    is_active = Column(Integer, default=0)
    status = Column(String, default="inactive")  # 'active', 'error', 'inactive'
    last_heartbeat = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Favourite(Base):
    __tablename__ = "favourites"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)


class Storage:
    def __init__(self, db_url: Optional[str] = None):
        # Prioritize constructor arg, then environment setting, then local SQLite
        self.db_url = db_url or settings.DATABASE_URL or "sqlite:///data/trading_bot.db"

        # Adjust connect_args for SQLite (required for multi-threading)
        connect_args = {}
        if self.db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

        self.engine = create_engine(self.db_url, connect_args=connect_args, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # QuestDB Configuration
        self.quest_host = settings.QUESTDB_HOST
        self.quest_port = settings.QUESTDB_PORT

    def save_tick_questdb(self, symbol, price, amount, side):
        """High-speed ingestion of market ticks using QuestDB ILP."""
        try:
            with Sender(self.quest_host, self.quest_port) as sender:
                sender.row(
                    "ticks",
                    symbols={"lp": "binance", "symbol": symbol},
                    columns={"price": float(price), "amount": float(amount), "side": side},
                    at=datetime.utcnow(),
                )
                sender.flush()
        except IngressError:
            # We don't want to crash the bot on logging errors
            pass

    def save_trade(self, symbol: str, side: str, amount: float, price: float, pnl: float = None):
        if self.degraded:
            print(f"OFFLINE TRADE: {side} {amount} {symbol} at {price}")
            return
        session = self.Session()
        trade = Trade(symbol=symbol, side=side, amount=amount, price=price, pnl=pnl)
        session.add(trade)
        session.commit()
        session.close()

    # --- Multi-Bot Methods ---

    def get_bot_configs(self, active_only=False):
        if self.degraded:
            return []
        session = self.Session()
        query = session.query(BotConfig)
        if active_only:
            query = query.filter(BotConfig.is_active == 1)
        configs = query.all()
        session.close()
        return configs

    def update_bot_config(self, symbol, strategy=None, params=None, is_active=None):
        if self.degraded:
            return
        session = self.Session()
        config = session.query(BotConfig).filter(BotConfig.symbol == symbol).first()
        if not config:
            config = BotConfig(symbol=symbol)
            session.add(config)

        if strategy:
            config.strategy = strategy
        if params:
            config.params = params
        if is_active is not None:
            config.is_active = 1 if is_active else 0

        session.commit()
        session.close()

    def get_favourites(self):
        session = self.Session()
        favs = session.query(Favourite).all()
        session.close()
        return [f.symbol for f in favs]

    def add_favourite(self, symbol):
        session = self.Session()
        if not session.query(Favourite).filter(Favourite.symbol == symbol).first():
            session.add(Favourite(symbol=symbol))
            session.commit()
        session.close()

    def remove_favourite(self, symbol):
        session = self.Session()
        fav = session.query(Favourite).filter(Favourite.symbol == symbol).first()
        if fav:
            session.delete(fav)
            session.commit()
        session.close()

    def get_trades(self):
        session = self.Session()
        trades = session.query(Trade).all()
        session.close()
        return trades

    def stop_all_bots(self):
        """Sets is_active to False for all bot configurations."""
        from .db import BotConfig

        session = self.Session()
        session.query(BotConfig).update({BotConfig.is_active: 0})
        session.commit()
        session.close()

    def get_bot_state(self):
        session = self.Session()
        state = session.query(BotState).first()
        if not state:
            state = BotState()
            session.add(state)
            session.commit()
            session.refresh(state)
        session.close()
        return state

    def get_bot_param_analytics(self):
        """Flatten complex strategy params into a relational view using PG 18 JSON_TABLE."""
        session = self.Session()
        # Raw SQL to utilize the futuristic JSON_TABLE feature
        sql = """
            SELECT * FROM bot_configs,
            JSON_TABLE(params::jsonb, '$'
                COLUMNS (
                    stop_loss_pct FLOAT PATH '$.stop_loss_pct',
                    take_profit_pct FLOAT PATH '$.take_profit_pct',
                    rsi_threshold INTEGER PATH '$.rsi_threshold'
                )
            ) AS jt
        """
        results = session.execute(text(sql)).fetchall()
        session.close()
        return results

    def update_bot_status(self, bot_id: int, status: str):
        """Update status using Enhanced RETURNING (PG 18) to get state diffs."""
        session = self.Session()
        # Using raw SQL to demonstrate the NEW/OLD RETURNING feature
        sql = """
            UPDATE bot_configs
            SET status = :status, last_heartbeat = :hb
            WHERE id = :id
            RETURNING OLD.status AS old_status, NEW.status AS new_status;
        """
        result = session.execute(
            text(sql), {"status": status, "hb": datetime.utcnow(), "id": bot_id}
        ).fetchone()
        session.commit()
        session.close()

        if result and result.old_status != result.new_status:
            print(f"Bot {bot_id} State Change: {result.old_status} -> {result.new_status}")

        return result

    def get_portfolio_metrics(self):
        """Calculate aggregate performance across all trades."""
        session = self.Session()
        trades = session.query(Trade).all()
        total_pnl = sum(t.pnl for t in trades if t.pnl) or 0.0
        active_bots = session.query(BotConfig).filter(BotConfig.is_active == 1).count()
        session.close()
        return {
            "total_pnl": round(total_pnl, 2),
            "active_bot_count": active_bots,
            "trade_count": len(trades),
        }

from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from questdb.ingress import Sender, IngressError

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    side = Column(String) # 'buy' or 'sell'
    amount = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pnl = Column(Float, nullable=True)

class OHLCV(Base):
    __tablename__ = 'ohlcv'
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    timestamp = Column(DateTime)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

class BotState(Base):
    __tablename__ = 'bot_state'
    id = Column(Integer, primary_key=True)
    is_running = Column(Integer, default=1) # 1=Running, 0=Stopped/Paused
    current_strategy = Column(String, default='advanced')
    symbol = Column(String, default='BTC/USDT')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BotConfig(Base):
    __tablename__ = 'bot_configs'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    strategy = Column(String, default='sma')
    params = Column(String, default='{}') # JSON string
    is_active = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Favourite(Base):
    __tablename__ = 'favourites'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)

class Storage:
    def __init__(self, db_url: str = 'sqlite:///data/trading_bot.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # QuestDB Configuration
        self.quest_host = os.getenv('QUESTDB_HOST', 'localhost')
        self.quest_port = int(os.getenv('QUESTDB_PORT', 9009))

    def save_tick_questdb(self, symbol, price, amount, side):
        """High-speed ingestion of market ticks using QuestDB ILP."""
        try:
            with Sender(self.quest_host, self.quest_port) as sender:
                sender.row(
                    'ticks',
                    symbols={'lp': 'binance', 'symbol': symbol},
                    columns={'price': float(price), 'amount': float(amount), 'side': side},
                    at=datetime.utcnow()
                )
                sender.flush()
        except IngressError as e:
            # We don't want to crash the bot on logging errors
            pass

    def save_trade(self, symbol: str, side: str, amount: float, price: float, pnl: float = None):
        session = self.Session()
        trade = Trade(symbol=symbol, side=side, amount=amount, price=price, pnl=pnl)
        session.add(trade)
        session.commit()
        session.close()

    # --- Multi-Bot Methods ---

    def get_bot_configs(self, active_only=False):
        session = self.Session()
        query = session.query(BotConfig)
        if active_only:
            query = query.filter(BotConfig.is_active == 1)
        configs = query.all()
        session.close()
        return configs

    def update_bot_config(self, symbol, strategy=None, params=None, is_active=None):
        session = self.Session()
        config = session.query(BotConfig).filter(BotConfig.symbol == symbol).first()
        if not config:
            config = BotConfig(symbol=symbol)
            session.add(config)
        
        if strategy: config.strategy = strategy
        if params: config.params = params
        if is_active is not None: config.is_active = 1 if is_active else 0
        
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

    def update_bot_state(self, is_running=None, strategy=None):
        session = self.Session()
        state = session.query(BotState).first()
        if not state:
            state = BotState()
            session.add(state)
        if is_running is not None:
            state.is_running = 1 if is_running else 0
        if strategy is not None:
            state.current_strategy = strategy
        session.commit()
        session.close()

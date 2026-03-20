from fastapi import FastAPI, HTTPException, Request, Form, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from storage.db import Storage
from storage.cache import Cache
import secrets
import uvicorn
import os
import asyncio
import json

app = FastAPI(title="Nice Trading Management API")
templates = Jinja2Templates(directory="api/templates")
storage = Storage()
cache = Cache()
security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("DASHBOARD_USER", "admin")
    correct_password = os.getenv("DASHBOARD_PASS", "password") # Default for demo
    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

class StateUpdate(BaseModel):
    is_running: bool = None
    strategy: str = None

# --- UI Routes ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user: str = Depends(get_current_user)):
    # Fetch all configs to show on dashboard
    bot_configs = storage.get_bot_configs()
    favourites = storage.get_favourites()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "bot_configs": bot_configs, 
        "favourites": favourites
    })

@app.get("/partials/bot-list", response_class=HTMLResponse)
async def get_bot_list(request: Request, user: str = Depends(get_current_user)):
    bot_configs = storage.get_bot_configs()
    return templates.TemplateResponse("partials/bot-list.html", {"request": request, "bot_configs": bot_configs})

@app.post("/bots/add")
async def add_bot(request: Request, symbol: str = Form(...), strategy: str = Form("sma"), user: str = Depends(get_current_user)):
    storage.update_bot_config(symbol=symbol, strategy=strategy, is_active=False)
    # Return updated list
    bot_configs = storage.get_bot_configs()
    return templates.TemplateResponse("partials/bot-list.html", {"request": request, "bot_configs": bot_configs})

@app.post("/bots/toggle/{symbol}")
async def toggle_bot(request: Request, symbol: str, user: str = Depends(get_current_user)):
    # Find current state and flip it
    configs = storage.get_bot_configs()
    current = next((c for c in configs if c.symbol == symbol), None)
    if current:
        new_state = not bool(current.is_active)
        storage.update_bot_config(symbol=symbol, is_active=new_state)
    
    bot_configs = storage.get_bot_configs()
    return templates.TemplateResponse("partials/bot-list.html", {"request": request, "bot_configs": bot_configs})

@app.get("/partials/favourites", response_class=HTMLResponse)
async def get_favs_partial(request: Request, user: str = Depends(get_current_user)):
    favourites = storage.get_favourites()
    return templates.TemplateResponse("partials/favourites.html", {"request": request, "favourites": favourites})

@app.post("/favourites/add")
async def add_fav(request: Request, symbol: str = Form(...), user: str = Depends(get_current_user)):
    storage.add_favourite(symbol)
    favourites = storage.get_favourites()
    return templates.TemplateResponse("partials/favourites.html", {"request": request, "favourites": favourites})

@app.post("/favourites/remove/{symbol}")
async def remove_fav(request: Request, symbol: str, user: str = Depends(get_current_user)):
    storage.remove_favourite(symbol)
    favourites = storage.get_favourites()
    return templates.TemplateResponse("partials/favourites.html", {"request": request, "favourites": favourites})

@app.post("/bots/stop-all")
async def stop_all_bots(request: Request, user: str = Depends(get_current_user)):
    """Deactivate all bots immediately."""
    storage.stop_all_bots()
    bot_configs = storage.get_bot_configs()
    return templates.TemplateResponse("partials/bot-list.html", {"request": request, "bot_configs": bot_configs})

@app.get("/partials/status-badge", response_class=HTMLResponse)
async def get_status_badge(request: Request):
    state = storage.get_bot_state()
    return templates.TemplateResponse("partials/status-badge.html", {"request": request, "state": state})

@app.get("/partials/control-panel", response_class=HTMLResponse)
async def get_control_panel(request: Request):
    state = storage.get_bot_state()
    return templates.TemplateResponse("partials/control-panel.html", {"request": request, "state": state})

@app.get("/partials/trades", response_class=HTMLResponse)
async def get_trades_partial(request: Request):
    trades = storage.get_trades()
    return templates.TemplateResponse("partials/trades.html", {"request": request, "trades": trades})

@app.get("/partials/stats", response_class=HTMLResponse)
async def get_stats_partial(request: Request):
    trades = storage.get_trades()
    total = len(trades)
    buys = len([t for t in trades if t.side == 'buy'])
    sells = len([t for t in trades if t.side == 'sell'])
    stats = {"total": total, "buys": buys, "sells": sells}
    return templates.TemplateResponse("partials/stats.html", {"request": request, "stats": stats})

# --- API & HTMX Action Routes ---

@app.post("/update")
async def update_status(
    request: Request,
    is_running: str = Form(None), 
    strategy: str = Form(None)
):
    # Handle both JSON and Form data for flexibility
    # HTMX sends Form data by default
    running_val = None
    if is_running is not None:
        running_val = is_running.lower() == 'true'
    
    storage.update_bot_state(is_running=running_val, strategy=strategy)
    
    # If it's an HTMX request, return the updated control panel fragment
    if request.headers.get("HX-Request"):
        state = storage.get_bot_state()
        return templates.TemplateResponse("partials/control-panel.html", {"request": request, "state": state})
    
    return {"message": "State updated successfully"}

# Keep the legacy API endpoints for compatibility
@app.get("/status")
def get_status_json():
    state = storage.get_bot_state()
    return {
        "is_running": bool(state.is_running),
        "current_strategy": state.current_strategy,
        "symbol": state.symbol,
        "updated_at": state.updated_at
    }

@app.get("/trades")
def get_trades_json():
    return storage.get_trades()

@app.get("/api/ohlcv/{symbol}")
async def get_ohlcv(symbol: str, user: str = Depends(get_current_user)):
    """Fetch historical OHLCV data for chart hydration."""
    connector = BinanceConnector('binance', os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_SECRET"))
    try:
        # In a production app, we would query QuestDB first
        # For now, we fetch from Binance via CCXT
        ohlcv_df = connector.fetch_ohlcv(symbol.replace('-', '/'))
        
        # Convert to Lightweight Charts format
        data = []
        for _, row in ohlcv_df.iterrows():
            data.append({
                "time": int(row['timestamp'].timestamp()),
                "open": row['open'],
                "high": row['high'],
                "low": row['low'],
                "close": row['close']
            })
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Real-Time Streaming ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/price")
async def websocket_price(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Fetch latest prices for all active bots
            bot_configs = storage.get_bot_configs(active_only=True)
            prices = {}
            for config in bot_configs:
                last_price = cache.get_last_price(config.symbol)
                if last_price:
                    prices[config.symbol] = last_price
            
            if prices:
                await websocket.send_text(json.dumps({"type": "price_update", "data": prices}))
            
            await asyncio.sleep(1) # Broadcast every second
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mock log streaming for demo
            await websocket.send_text(json.dumps({"type": "log", "data": "Bot heartbeat active..."}))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 🏠 Local Server Setup

This guide explains how to run the full trading suite on your local machine for development, testing, or dry-running strategies.

## 🐳 Option 1: Docker (Recommended)
This is the fastest and cleanest way to run the entire stack.

1.  **Ensure Docker is running**.
2.  **Build and Start**:
    ```bash
    docker-compose up --build -d
    ```
3.  **Access the Dashboard**:
    Open `http://localhost:80` (or `http://localhost:8000` if bypassing Nginx).

### Viewing Internal Logs
```bash
# View all logs
docker-compose logs -f

# View only the bot manager
docker logs -f nice-trading-manager-1
```

## 👩‍💻 Option 2: Manual (Development Mode)
Useful if you want to debug individual components without containers.

### 1. Services
You must have **Redis** and **QuestDB** running locally.
*   QuestDB: `docker run -p 9000:9000 -p 9009:9009 questdb/questdb`
*   Redis: `brew install redis && brew services start redis`

### 2. Application
Run the components in separate terminals:
```bash
# Terminal 1: API
uvicorn api.app:app --reload

# Terminal 2: Manager
python manager/bot_manager.py

# Terminal 3: Data Worker
python workers/orderbook_fetcher.py
```

## 🛡️ Initial Data Check
Once running, verify your setup:
1.  **QuestDB UI**: Visit `http://localhost:9000` and run `select * from ticks` to see incoming market data.
2.  **Dashboard**: Add a bot (e.g., `ETH/USDT`) and verify you see the live price updating every few seconds.

# 🤖 Nice Trading Platform: Institutional-Grade Multi-Bot Suite

A high-performance, private trading ecosystem designed for algorithmic execution, real-time monitoring, and institutional safety. Built on Python 3.11, PostgreSQL 18, Go (Low-latency), and HTMX.

---

## 🚀 Key Features

### 🏢 Multi-Bot Orchestration
*   **Isolated Execution**: Each bot runs in its own process, ensuring that a single symbol's failure doesn't affect the fleet.
*   **Dynamic Management**: Start, stop, and configure strategies (SMA, MACD, Advanced) for any symbol in seconds.
*   **Asset Favorites**: Keep your preferred tickers pinned to the top of your cockpit.

### 📊 High-Performance Data Layer
*   **PostgreSQL 18 Multi-Layered**: Consolidation of persistent storage (Trades) and ultra-low latency caching (UNLOGGED orderbook tables).
*   **Go-Powered Ingestion**: Native performance worker for sub-millisecond market updates.
*   **QuestDB Time-Series**: Professional-grade tick ingestion for quantitative analysis.
*   **Lightweight Charts**: Professional-grade charting with real-time WebSocket updates and signal markers (Buy/Sell).

### 🛡️ Institutional-Grade Safety
*   **Pydantic Settings**: Centralized, validated configuration for API keys and host settings.
*   **Live Balance Sync**: Real-time position sizing based on live Binance capital.
*   **Exchange-Side Safety (TP/SL)**: Orders are persisted directly on the exchange for crash-resistance.
*   **Global Circuit Breaker**: Automated and manual "Kill Switches" to stop everything during extreme volatility.
*   **Basic Auth Security**: Password-protected dashboard and API.

---

## 📁 System Architecture

```text
nice-trading/
├── api/                   # HTMX/FastAPI Web Dashboard
├── manager/               # Multi-bot Management & Execution
├── engine/                # Vectorized Indicators & Strategy Logic
├── workers/               # Ingestion Workers (Go + Python)
├── connectors/            # CCXT Wrapper for Exchange Connectivity
├── storage/               # PostgreSQL 18 & QuestDB Persistence
├── nginx/                 # Production Reverse Proxy Gateway
└── docs/                  # Detailed Technical Documentation
```

---

## 🛠️ Operational Cockpit

We use a `Makefile` to unify our hybrid Python/Go/Docker workflow.

### 1. Local Development
1.  **Install dependencies**: `make install`
2.  **Run Dashboard**: `make run-api`
3.  **Run Go Worker**: `make run-go-worker`
4.  **Execute Tests**: `make test`

### 2. Docker Deployment
1.  **Configure environment**: `cp .env.example .env` (Add your Binance Keys).
2.  **Launch the fleet**: `make up`
3.  **Follow the logs**: `make logs`
4.  **Shutdown**: `make down`

---

## 📚 Documentation
For a deep dive into the system, check our professional documentation:
*   **Getting Started**: [Local Setup](./docs/getting-started/local-setup.md) | [Onboarding](./docs/getting-started/onboarding.md) | [Lightsail Deployment](./docs/getting-started/lightsail-deployment.md)
*   **User Guide**: [User Manual](./docs/user-guide/manual.md) | [Safety Audit](./docs/user-guide/readiness-audit.md)
*   **Architecture**: [System Overview](./docs/architecture/architecture-overview.md) | [Tech Stack](./docs/architecture/tech-stack.md)
*   **Research**: [Future Roadmap](./docs/research/future-roadmap.md) | [Gap Analysis](./docs/research/gap-analysis.md)

---
*Created with ❤️ for quantitative excellence.*

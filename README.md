# 🤖 Nice Trading Platform: Institutional-Grade Multi-Bot Suite

A high-performance, private trading ecosystem designed for algorithmic execution, real-time monitoring, and institutional safety. Built on Python, QuestDB, Redis, and HTMX.

---

## 🚀 Key Features

### 🏢 Multi-Bot Orchestration
*   **Isolated Execution**: Each bot runs in its own process, ensuring that a single symbol's failure doesn't affect the fleet.
*   **Dynamic Management**: Start, stop, and configure strategies (SMA, MACD, Advanced) for any symbol in seconds.
*   **Asset Favorites**: Keep your preferred tickers pinned to the top of your cockpit.

### 📊 High-Performance Data Layer
*   **QuestDB Time-Series**: Microsecond-level tick ingestion for every symbol.
*   **Redis Cache**: Ultra-low latency orderbook storage for high-frequency signal generation.
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
├── connectors/            # CCXT Wrapper for Exchange Connectivity
├── storage/               # QuestDB, Redis, & SQLite Data Persistence
├── nginx/                 # Production Reverse Proxy Gateway
└── docs/                  # Detailed Technical Documentation
```

---

## 🛠️ Quick Start

### 1. Local Environment (Docker)
1.  Configure your environment: `cp .env.example .env` (Add your Binance Keys).
2.  Launch the fleet: `docker-compose up --build -d`.
3.  Monitor the Cockpit: `http://localhost:80` (Default: admin / password).

### 2. Remote Deployment (AWS Lightsail)
1.  Setup your VM: `/bin/bash setup_lightsail.sh`.
2.  Deploy from local: `./deploy.sh [VM_IP] [SSH_KEY_PATH]`.

---

## 📚 Documentation
For a deep dive into the system, check our professional documentation:
*   **Getting Started**: [Local Setup](./docs/getting-started/local-setup.md) | [Onboarding](./docs/getting-started/onboarding.md) | [Lightsail Deployment](./docs/getting-started/lightsail-deployment.md)
*   **User Guide**: [User Manual](./docs/user-guide/manual.md) | [Safety Audit](./docs/user-guide/readiness-audit.md)
*   **Architecture**: [Tech Stack](./docs/architecture/tech-stack.md) | [Design Overview](./docs/architecture/implementation-plan.md) | [Component Design](./docs/architecture/low-level-design.md)
*   **Research**: [Future Roadmap](./docs/research/future-roadmap.md) | [TSDB Research](./docs/research/database-research.md)

---
*Created with ❤️ for quantitative excellence.*

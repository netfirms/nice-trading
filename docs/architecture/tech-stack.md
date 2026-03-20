# 🛠️ Technology Stack

The Nice Trading Platform is built using a modern, high-performance stack selected for low-latency execution and high-frequency data ingestion.

## 🐍 Backend (Core & Strategy)
*   **Language**: Python 3.10+
*   **Libraries**:
    *   `CCXT`: For exchange connectivity and order execution.
    *   `Pandas` & `NumPy`: For vectorized technical indicator calculations.
    *   `SQLAlchemy`: ORM for configuration and trade history persistence.
    *   `Multiprocessing`: Parallel execution architecture for multi-bot isolation.

## ⚡ Data & Streaming
*   **QuestDB**: High-performance time-series database for tick-level market data storage.
*   **Redis**: In-memory data store for low-latency orderbook caching and worker communication.
*   **FastAPI WebSockets**: Real-time bidirectional streaming for UI price and log updates.

## 🎨 Frontend (Cockpit)
*   **HTMX**: Reactive, AJAX-driven UI without the overhead of a heavy JavaScript framework.
*   **FastAPI (Jinja2)**: Server-side rendering for speed and SEO.
*   **Tailwind CSS**: Utility-first styling for the "Trading Cockpit" aesthetic.
*   **Lightweight Charts**: High-performance financial charts for real-time visualization.

## 🐋 Infrastructure & DevOps
*   **Docker & Docker Compose**: Unified container orchestration.
*   **Nginx**: Production-grade reverse proxy and security gateway.
*   **AWS Lightsail**: Recommended production host for its cost-effective fixed pricing.
*   **Telegram API**: Proactive alerting system for trade execution and system health.

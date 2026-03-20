# Nice Trading Platform 🚀

A professional, multi-bot, event-driven trading platform built for high-performance crypto trading on Binance.

## Key Features
-   **Multi-Bot Management**: Run multiple strategies and assets simultaneously.
-   **High-Performance Cache**: Redis-backed L2 orderbook for sub-millisecond price access.
-   **Time-Series Storage**: QuestDB for high-speed tick ingestion and OHLCV analytics.
-   **Simple Web Dashboard**: Lightweight HTMX + FastAPI UI with integrated TradingView charts.
-   **Fully Containerized**: Orchestrated with Docker Compose for easy deployment.

## Documentation 📖
All technical documentation is located in the [docs/](docs/) directory:
-   **[Implementation Plan](docs/implementation_plan.md)**: Current roadmap and feature progress.
-   **[Architecture (High-Level)](docs/architecture/high_level.md)**: System overview and external connections.
-   **[Architecture (Low-Level)](docs/architecture/low_level.md)**: Component interactions and process management.
-   **[Walkthrough](docs/walkthrough.md)**: Step-by-step guide to running the platform.
-   **[Research](docs/research/)**: Deep dives into time-series databases and advanced trading stacks.
-   **[Gap Analysis](docs/gap_analysis.md)**: Product requirement tracking.

## Getting Started 🛠️

1.  **Configure Environment**:
    Create a `.env` file based on `.env.example` with your Binance API keys.

2.  **Start Services**:
    ```bash
    docker-compose up --build -d
    ```

3.  **Access Dashboard**:
    Visit `http://localhost:8000` to manage your bots.

4.  **View Data**:
    Visit `http://localhost:9000` for the QuestDB Web Console.

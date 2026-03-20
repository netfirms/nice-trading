# Detailed Architecture: Nice Trading Platform

This document provides a deep dive into the system's design, from high-level orchestration to low-level component interactions.

## 1. High-Level Architecture (System Overview)

This diagram shows the major blocks and how they interact with external services and the user.

```mermaid
graph TD
    User((User)) <--> UI["HTMX Web Dashboard (FastAPI)"]
    
    subgraph "Application Layer"
        UI <--> Manager["Bot Manager (Orchestrator)"]
        Manager -- Spawns --> Runner1["Bot Runner (BTC)"]
        Manager -- Spawns --> Runner2["Bot Runner (ETH)"]
    end

    subgraph "Data Layer"
        Runner1 & Runner2 -- Writes Ticks --> QuestDB[("QuestDB (Time-Series)")]
        Runner1 & Runner2 -- Reads L2 --> Redis[("Redis (L2 Cache)")]
        UI & Manager <--> SQLite[("SQLite (Bot Registry / Trades)")]
    end

    subgraph "External"
        Worker["Market Data Worker"] -- Streams --> Redis
        Worker <--> Binance["Binance API"]
        Runner1 & Runner2 <--> Binance
    end
```

## 2. Low-Level Architecture (Process & Component)

This diagram details the internal logic of a single **Bot Runner** instance and how it uses the specialized storage modules.

```mermaid
graph TD
    subgraph "Bot Runner Instance"
        SM["Strategy Manager"] --> |Signal| RM["Risk Manager"]
        RM --> |Validation| Ex["Execution Engine"]
        OHLCV["OHLCV Aggregator"] --> SM
    end

    subgraph "Storage Interconnect"
        Ex -- save_trade --> DB["SQLite (Persistent)"]
        Ex -- save_tick --> QDB["QuestDB (ILP)"]
        OHLCV -- get_last_price --> RDS["Redis"]
    end

    subgraph "External Connectors"
        Ex <--> CCXT["Binance Connector"]
        OHLCV <--> CCXT
    end
```

## 3. Data Flow & Networking

| Flow Type | Source | Destination | Protocol | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Market Data** | Binance | Local Worker | REST/WS | Real-time price and L2 orderbook ingestion. |
| **Cache** | Worker | Redis | RESP | Sub-millisecond orderbook updates. |
| **Ingestion** | Bot/Worker | QuestDB | ILP (Line Protocol) | High-throughput time-series tick logging. |
| **Control** | Web UI | SQLite | SQL | Updating bot configurations and favorites. |
| **Orchestration**| Manager | Sub-processes | Signals | Starting/Stopping bot instances via Multiprocessing. |

## 4. Deployment Architecture (Docker)

All services are isolated in Docker containers within a shared bridge network.

*   **Service: `api`**: Runs the FastAPI server (Port 8000).
*   **Service: `manager`**: Runs the Bot Manager service.
*   **Service: `worker`**: Runs the high-frequency market data fetcher.
*   **Service: `redis`**: High-speed memory store.
*   **Service: `questdb`**: Low-latency time-series database.
*   **Volume: `trading_data`**: Persists the SQLite database and logs across container restarts.

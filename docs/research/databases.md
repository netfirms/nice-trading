# Research Notes: High-Performance Local Time-Series Databases

For a private trading platform, moving beyond SQLite is necessary when handling high-frequency tick data or large-scale historical backtesting.

## 1. Top Candidates for Local Deployment

| Database | Best For | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **QuestDB** | **High-Frequency Ingestion** | Extremely fast (C++/Java), SQL support, lightweight, built-in OHLCV functions. | Smaller ecosystem than Postgres. |
| **TimescaleDB** | **Reliability & SQL Power** | Based on PostgreSQL, full SQL support, automatic partitioning (hypertables), great for metadata + price data. | Higher memory overhead than QuestDB. |
| **ClickHouse** | **Massive Analytics** | Columnar storage, incredibly fast for querying billions of rows (backtesting), great compression. | Can be overkill for a single-user "small robot." |
| **DuckDB** | **Local File Analysis** | Embedded (like SQLite but for Big Data), works directly with Parquet/CSV, no server needed. | Not ideal for concurrent real-time writes. |
| **Kdb+** | **Institutional HFT** | The industry standard, vectorized execution, extreme speed. | Proprietary, steep learning curve (q language), expensive. |

## 2. Recommendations

### Recommendation A: QuestDB (Speed & Simplicity)
If you want the absolute highest ingestion speed for raw tick data with a simple SQL interface, **QuestDB** is the winner. It was designed specifically for financial services and is very efficient at calculating OHLC bars from raw trades.

### Recommendation B: TimescaleDB (Versatility)
If you need to join your price data with complex metadata (e.g., wallet info, project fundamentals, user settings) and want to stay within the familiar PostgreSQL ecosystem, **TimescaleDB** is the most robust choice.

### Recommendation C: DuckDB (Backtesting)
For local backtesting where you store historical data in **Parquet** files, **DuckDB** is an incredible "analytical SQLite" that requires no server and performs extremely well for research.

## 3. Integrating with your Platform
In the next phase, we can add a service to the `docker-compose.yml` (e.g., `questdb`) and update the `Storage` module to use a specialized driver for high-volume writes.

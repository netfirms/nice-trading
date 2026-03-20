# 📘 User Manual: Nice Trading Platform

Welcome to your private trading fleet. This document provides a solid overview of how to operate and maintain your institutional-grade trading robot.

## 🕹️ The Trading Cockpit (Dashboard)

The dashboard is your central mission control, built with low-latency HTMX.

### 🔹 Bot Management
*   **System Badge**: Shows the "Live" heartbeat of the manager. If it turns grey, check the `manager` container logs.
*   **Emergency Stop**: The red button on the top right stops all active processes and resets the database state to `inactive`.
*   **Add Bot**: Use the input to add a new symbol (e.g., `BTC/USDT`) and select a strategy.

### 🔹 Real-Time Charting
*   **Signal Markers**: When a bot detects an EMA Crossover or RSI signal, a marker appears directly on the chart (Arrow Up/Down).
*   **Live Price**: The price displayed in the bot list is streamed via WebSockets from the `orderbook-worker`.

---

## 🛡️ Safety & Risk Controls

The platform is designed to protect your capital above all else.

### ⚡ Exchange-Side Exit
Our system doesn't just watch prices locally. When a trade is executed:
1.  An **Entry Order** is placed on Binance.
2.  A **Stop-Loss Limit** order is immediately placed on Binance.
This ensures that even if our server loses power, your exit strategy is already "In the exchange's hands."

### 🛑 Circuit Breaker
Every `RiskManager` instance calculates the current drawdown relative to your "Initial Day Balance." If we hit **-5%**, the bot will refuse to take new signals and alert you via Telegram.

---

## ⚙️ Advanced Configuration

### `config.yaml`
Fine-tune global parameters:
*   `log_level`: Default is `INFO`. Switch to `DEBUG` for deep troubleshooting.
*   `max_retries`: Number of times to retry a failed CCXT call.

### `.env`
Sensitive secrets:
*   `BINANCE_API_KEY`: Required for live trading.
*   `TELEGRAM_BOT_TOKEN`: Enable this for mobile push alerts.
*   `DASHBOARD_PASS`: Secure your web access.

---

## 🛠️ Maintenance & Troubleshooting

### Viewing Logs
To see what a specific bot is thinking:
```bash
docker logs --tail 50 -f nice-trading-manager-1
```

### Resetting Data
To clear QuestDB and start fresh:
```bash
docker-compose down -v
```

---
*Disclaimer: Trading involves risk. Ensure you have tested your strategies in DRY RUN mode before deploying real capital.*

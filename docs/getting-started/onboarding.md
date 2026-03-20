# 👋 Developer Onboarding

Welcome to the **Nice Trading Platform** development team! This guide will get you up to speed with our architecture and workflow.

## 🏗️ Architecture Overview
The system follows a **Worker-Manager-API** pattern:
1.  **Workers**: Independent processes that fetch data (e.g., `orderbook_fetcher.py`).
2.  **Manager**: Orchestrates multiple `BotRunner` processes based on DB configurations.
3.  **API**: Serves the HTMX dashboard and provides endpoints for control.

## 🛠️ Development Setup

### 1. Prerequisites
*   Python 3.10+
*   Docker & Docker Compose
*   A Binance Testnet account (optional but recommended)

### 2. Initial Setup
```bash
git clone git@github.com:netfirms/nice-trading.git
cd nice-trading
python -m venv venv
source venv/bin/activate
pip install -e .
```

### 3. Environment Config
Copy `.env.example` to `.env` and fill in your keys. Use `DASHBOARD_PASS` to secure your local UI.

## 🧪 Running Tests
We use `pytest` for unit testing our core modules:
```bash
pytest tests/
```

## 📜 Coding Standards
*   **Safety First**: Always wrap exchange calls in the `@retry_on_failure` decorator.
*   **Process Isolation**: Avoid shared global state between bots; use Redis or the Database for communication.
*   **Logging**: Use the structured `utils.logger` for all output.

---
*Happy Coding! For any questions, refer to the [Architecture Overview](../architecture/implementation-plan.md).*

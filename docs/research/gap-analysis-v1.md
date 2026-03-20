# Gap Analysis: Nice Trading Platform

This document identifies the missing pieces required to transition from a single-bot script to a full-featured "Robot Trading Platform."

## Requirement Check-list

| Requirement | Current Status | Gap |
| :--- | :---: | :--- |
| **View asset price (chart)** | ⚠️ Partial | We have the data (QuestDB/Redis) but no visual charts (e.g., Lightweight Charts). |
| **Add price favourite per asset** | ❌ Gap | Need a `Favourites` table in SQLite and UI toggles. |
| **Create bot per asset/strategy** | ❌ Gap | Current logic is single-process. Need a `BotManager` to spawn/manage multiple bot instances. |
| **Audit bot (logs) per asset** | ⚠️ Partial | Logs exists, but need filtering by Bot ID/Asset in the UI. |
| **Design own strategy** | ⚠️ Partial | System is modular (Python classes), but needs a UI for parameter tuning or a "Strategy Builder." |
| **Backtest strategy per asset** | ✅ Implemented | Engine exists; needs integration into the new HTMX Dashboard. |
| **Run multiple bots simultaneously** | ❌ Gap | Infrastructure supports it, but the orchestration (starting multiple processes) is missing. |
| **Audit all bots (live feed)** | ⚠️ Partial | Current trade table polls; needs a unified "Live Activity" feed from all running instances. |
| **Mobile/Tablet friendly** | ⚠️ Partial | Using Tailwind (responsive), but UI layouts need specific mobile optimization. |

## Immediate Priorities (Gap Fillers)

1.  **Multi-Bot Architecture**: Move from `main.py` (single bot) to a `BotManager` that can spawn multiple instances based on configurations in the database.
2.  **Charting Integration**: Integrate TradingView-style charts (using `Lightweight Charts` or `Chart.js`) to visualize QuestDB/Redis data.
3.  **Bot Registry**: Create a `bots` table in SQLite to store: `id`, `asset`, `strategy_name`, `params`, `is_active`.
4.  **Live Log Aggregator**: A dedicated page/fragment aggregating trades and logs from all active bot IDs.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Trading Platform that integrates Alpaca Markets paper trading with task management and backtesting capabilities. The codebase is split across Python backend (trading engine, task managers, API integrations) and JavaScript frontend (web-based task hub).

## Architecture

### Core Components

**Trading Layer** (`trading_*.py`)
- `alpaca_integration.py` - REST wrapper for Alpaca Markets API (accounts, positions, orders, market data)
- `alpha_vantage_integration.py` - Technical indicators and historical data from Alpha Vantage
- `trading_strategy.py` - Base strategy implementation with signal generation
- `backtesting_engine.py` - Monte Carlo backtesting with commission/slippage simulation
- `qullamaggie_momentum_strategy.py` - Specific momentum-based trading strategy
- `config.py` - Centralized configuration with environment variable loading (API keys, risk parameters)

**Task Management**
- `task_manager.py` (32KB) - Full-featured desktop task manager using tkinter with categories, priorities, due dates, tags
- `final_task_manager.py` - Simplified task manager variant
- `simple_task_manager.py` - Minimal task manager implementation

**Desktop Dashboards**
- `trading_dashboard.py` - Multi-tab tkinter dashboard integrating live trading data, strategy backtesting, performance metrics, and market data
- `simple_trading_dashboard.py` - Lightweight dashboard alternative

**Web Interface**
- `app.js` - Task hub web app (TodoApp class) with filtering, search, import/export, dark mode
- `task-hub.html/css/js` - Web-based task management interface
- `index.html` - Dashboard web view

**Utilities**
- `git-integration.py`, `github-integration.py` - Git and GitHub API helpers for automation
- `auto-git-workflow.py` - Automated commit/push workflows
- `rg-alt.py`, `jq-alt.py` - Ripgrep and jq-like utilities

### Data Flow

1. **Trading Pipeline**: Config → AlpacaIntegration (connect to account) → MarketData (Alpha Vantage) → TradingStrategy (signals) → BacktestingEngine (simulation) → Dashboard (visualization)
2. **Task Management**: JSON file storage (tasks.json) ↔ Task classes → UI (tkinter or web)

## Common Commands

### Setup & Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# For development with virtual environment
python -m venv dashboard_env
source dashboard_env/bin/activate
pip install -r requirements.txt

# Validate configuration (checks API keys)
python config.py
```

### Running Applications

**Desktop Task Manager** (primary application)
```bash
python task_manager.py
```

**Trading Dashboard** (standalone)
```bash
python trading_dashboard.py
```

**Backtesting** (to evaluate strategy performance)
```bash
python backtesting_engine.py
```

**Web Task Hub** (open `task-hub.html` in browser or serve via HTTP)

### Testing & Validation

There are no formal unit tests. Validation is manual:
- Check Alpaca connection: `python alpaca_integration.py` (instantiates connection, logs on success)
- Validate config: `python config.py` (validates API keys are set)
- Test trading strategy: Run backtesting_engine.py with historical data

## Key Development Patterns

### Configuration Management
- All settings live in `config.py` - loaded from environment variables via `python-dotenv`
- API keys must be in `.env` file or environment: `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPHA_VANTAGE_API_KEY`
- Risk parameters (position size, stop loss, take profit) are defined in config.py
- Paper trading URL hardcoded to `https://paper-api.alpaca.markets` for safety

### Logging
- Uses Python `logging` module configured in each integration
- Log level set via `LOG_LEVEL` in config.py (default: 'INFO')
- Log file: `trading_log.txt`

### Data Storage
- Tasks stored in `tasks.json` (JSON format, human-readable)
- Backups created in `backups/` directory with timestamp
- Memory/context stored in `memory/` subdirectory

### Error Handling
- AlpacaIntegration logs connection errors but raises exceptions for critical failures
- Trading operations include try/except with logging before returning None/empty data

## Important Notes

### API Configuration
- **Paper Trading Only**: Alpaca API hardcoded to paper trading endpoint for safety
- **Rate Limiting**: Alpha Vantage has rate limits (typically 5 requests/min for free tier) - backoff strategy implemented
- **Market Hours**: Alpaca market data only available during market hours (9:30-16:00 ET)

### Dependencies
- **Core Trading**: `alpaca-trade-api`, `alpha-vantage`, `pandas`, `numpy`
- **UI**: `tkinter` (built-in), `matplotlib` for charts (fallback to `simple_plotting.py` if unavailable)
- **Web**: Vanilla JavaScript (no framework), uses localStorage for task persistence
- **Utilities**: `requests`, `websocket-client`, `python-dotenv`

### Code Organization Philosophy
The codebase reflects human-AI collaboration principles (see `CONTRIBUTING.md`):
- Clear, self-documenting variable names
- Comments explain complex logic (especially in backtesting_engine.py calculations)
- Multiple implementations (simple vs. featured) for flexibility
- Separate utilities for git/GitHub automation (used by CI/CD)

### Desktop Environment
- Tkinter apps require X11 display or suitable desktop environment
- For headless environments, use web interface or export data via API
- Threading used in trading_dashboard.py for non-blocking data updates

## File Size Reference

For context on module scope:
- `task_manager.py` (32KB) - Full-featured desktop app
- `trading_dashboard.py` (29KB) - Rich dashboard with multiple data sources
- `backtesting_engine.py` (22KB) - Complex simulation with statistics
- Configuration & simple utilities: 2-7KB each

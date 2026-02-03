# Alpaca Trading Platform Integration

This project provides a complete integration with Alpaca Markets API for paper trading, including market data retrieval, order placement, and position monitoring.

## Features
- Paper trading account integration
- Real-time market data retrieval
- Order placement and management
- Position monitoring
- Technical indicators via Alpha Vantage
- Configuration management
- Basic trading strategy template

## Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Configure API keys in `config.py`
3. Test connection: `python test_connection.py`
4. Run basic strategy: `python trading_strategy.py`

## Files
- `config.py` - API configuration and keys
- `alpaca_integration.py` - Core Alpaca API wrapper
- `alpha_vantage_integration.py` - Technical indicators
- `trading_strategy.py` - Basic strategy template
- `test_connection.py` - Connection and functionality tests
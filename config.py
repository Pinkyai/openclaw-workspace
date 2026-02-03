import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alpaca API Configuration
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', 'your_paper_api_key_here')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', 'your_paper_secret_key_here')
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'  # Paper trading URL
ALPACA_DATA_URL = 'https://data.alpaca.markets'

# Alpha Vantage API Configuration
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'your_alpha_vantage_key_here')

# Trading Configuration
DEFAULT_TIMEFRAME = '1Min'
DEFAULT_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
PAPER_TRADING = True  # Always use paper trading for safety

# Risk Management
MAX_POSITION_SIZE = 0.1  # Maximum 10% of portfolio per position
MAX_PORTFOLIO_RISK = 0.05  # Maximum 5% portfolio risk
STOP_LOSS_PERCENTAGE = 0.02  # 2% stop loss
TAKE_PROFIT_PERCENTAGE = 0.05  # 5% take profit

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'trading_log.txt'

def validate_config():
    """Validate that required configuration is present"""
    if ALPACA_API_KEY == 'your_paper_api_key_here':
        raise ValueError("Please set your Alpaca API key in config.py or .env file")
    if ALPACA_SECRET_KEY == 'your_paper_secret_key_here':
        raise ValueError("Please set your Alpaca secret key in config.py or .env file")
    if ALPHA_VANTAGE_API_KEY == 'your_alpha_vantage_key_here':
        print("Warning: Alpha Vantage API key not set. Technical indicators will be limited.")
    
    print("✓ Configuration validated successfully")

if __name__ == "__main__":
    validate_config()
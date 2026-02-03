import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
import time
from config import *

# Set up logging
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlphaVantageIntegration:
    """Alpha Vantage API integration for technical indicators"""
    
    def __init__(self, api_key=None):
        """Initialize Alpha Vantage API connection"""
        self.api_key = api_key or ALPHA_VANTAGE_API_KEY
        self.base_url = 'https://www.alphavantage.co/query'
        
        if self.api_key == 'your_alpha_vantage_key_here':
            logger.warning("Alpha Vantage API key not configured. Some features will be limited.")
    
    def get_technical_indicator(self, symbol, indicator, interval='1min', time_period=20, series_type='close'):
        """Get technical indicator from Alpha Vantage"""
        try:
            params = {
                'function': indicator,
                'symbol': symbol,
                'interval': interval,
                'time_period': time_period,
                'series_type': series_type,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract the indicator data
            indicator_key = f'Technical Analysis: {indicator.replace("_", " ").title()}'
            if indicator_key in data:
                return pd.DataFrame.from_dict(data[indicator_key], orient='index')
            else:
                logger.warning(f"No data found for {indicator}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting {indicator} for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_sma(self, symbol, interval='1min', time_period=20, series_type='close'):
        """Get Simple Moving Average"""
        return self.get_technical_indicator(symbol, 'SMA', interval, time_period, series_type)
    
    def get_ema(self, symbol, interval='1min', time_period=20, series_type='close'):
        """Get Exponential Moving Average"""
        return self.get_technical_indicator(symbol, 'EMA', interval, time_period, series_type)
    
    def get_rsi(self, symbol, interval='1min', time_period=14, series_type='close'):
        """Get Relative Strength Index"""
        return self.get_technical_indicator(symbol, 'RSI', interval, time_period, series_type)
    
    def get_macd(self, symbol, interval='1min', series_type='close', fastperiod=12, slowperiod=26, signalperiod=9):
        """Get MACD (Moving Average Convergence Divergence)"""
        try:
            params = {
                'function': 'MACD',
                'symbol': symbol,
                'interval': interval,
                'series_type': series_type,
                'fastperiod': fastperiod,
                'slowperiod': slowperiod,
                'signalperiod': signalperiod,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Technical Analysis: MACD' in data:
                return pd.DataFrame.from_dict(data['Technical Analysis: MACD'], orient='index')
            else:
                logger.warning(f"No MACD data found for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting MACD for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_bollinger_bands(self, symbol, interval='1min', time_period=20, series_type='close', nbdevup=2, nbdevdn=2):
        """Get Bollinger Bands"""
        try:
            params = {
                'function': 'BBANDS',
                'symbol': symbol,
                'interval': interval,
                'time_period': time_period,
                'series_type': series_type,
                'nbdevup': nbdevup,
                'nbdevdn': nbdevdn,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Technical Analysis: BBANDS' in data:
                return pd.DataFrame.from_dict(data['Technical Analysis: BBANDS'], orient='index')
            else:
                logger.warning(f"No Bollinger Bands data found for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting Bollinger Bands for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_stochastic(self, symbol, interval='1min', fastkperiod=5, slowkperiod=3, slowdperiod=3):
        """Get Stochastic Oscillator"""
        try:
            params = {
                'function': 'STOCH',
                'symbol': symbol,
                'interval': interval,
                'fastkperiod': fastkperiod,
                'slowkperiod': slowkperiod,
                'slowdperiod': slowdperiod,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Technical Analysis: STOCH' in data:
                return pd.DataFrame.from_dict(data['Technical Analysis: STOCH'], orient='index')
            else:
                logger.warning(f"No Stochastic data found for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting Stochastic for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_atr(self, symbol, interval='1min', time_period=14):
        """Get Average True Range"""
        return self.get_technical_indicator(symbol, 'ATR', interval, time_period, 'close')
    
    def get_obv(self, symbol, interval='1min'):
        """Get On Balance Volume"""
        try:
            params = {
                'function': 'OBV',
                'symbol': symbol,
                'interval': interval,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Technical Analysis: OBV' in data:
                return pd.DataFrame.from_dict(data['Technical Analysis: OBV'], orient='index')
            else:
                logger.warning(f"No OBV data found for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting OBV for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_intraday_data(self, symbol, interval='1min', outputsize='compact'):
        """Get intraday market data"""
        try:
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            time_series_key = f'Time Series ({interval})'
            if time_series_key in data:
                return pd.DataFrame.from_dict(data[time_series_key], orient='index')
            else:
                logger.warning(f"No intraday data found for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting intraday data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_all_indicators(self, symbol, interval='1min'):
        """Get all available technical indicators for a symbol"""
        indicators = {}
        
        if self.api_key == 'your_alpha_vantage_key_here':
            logger.warning("Alpha Vantage API key not configured. Skipping technical indicators.")
            return indicators
        
        try:
            # Get common indicators
            indicators['sma_20'] = self.get_sma(symbol, interval, 20)
            indicators['sma_50'] = self.get_sma(symbol, interval, 50)
            indicators['ema_20'] = self.get_ema(symbol, interval, 20)
            indicators['rsi'] = self.get_rsi(symbol, interval, 14)
            indicators['macd'] = self.get_macd(symbol, interval)
            indicators['bbands'] = self.get_bollinger_bands(symbol, interval)
            indicators['stoch'] = self.get_stochastic(symbol, interval)
            indicators['atr'] = self.get_atr(symbol, interval)
            indicators['obv'] = self.get_obv(symbol, interval)
            
            logger.info(f"Retrieved {len(indicators)} technical indicators for {symbol}")
            return indicators
            
        except Exception as e:
            logger.error(f"Error getting all indicators for {symbol}: {e}")
            return indicators

if __name__ == "__main__":
    # Test Alpha Vantage integration
    av = AlphaVantageIntegration()
    
    # Test with demo data (requires API key for real data)
    print("Testing Alpha Vantage integration...")
    
    # Get RSI for AAPL (if API key is configured)
    rsi_data = av.get_rsi('AAPL')
    if not rsi_data.empty:
        print(f"RSI data points: {len(rsi_data)}")
    else:
        print("No RSI data available (check API key)")
    
    print("Alpha Vantage integration test completed")
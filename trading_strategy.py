import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from alpaca_integration import AlpacaIntegration
from alpha_vantage_integration import AlphaVantageIntegration
from config import *

# Set up logging
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingStrategy:
    """Basic trading strategy template with risk management"""
    
    def __init__(self):
        """Initialize trading strategy"""
        self.alpaca = AlpacaIntegration()
        self.alpha_vantage = AlphaVantageIntegration()
        self.positions = {}
        self.orders = []
        
        logger.info("Trading strategy initialized")
    
    def calculate_position_size(self, symbol, account_value, risk_per_trade=0.01):
        """Calculate position size based on risk management"""
        try:
            # Get current price
            market_data = self.alpaca.get_market_data(symbol, limit=1)
            if market_data.empty:
                return 0
            
            current_price = market_data['close'].iloc[-1]
            
            # Get ATR for stop loss calculation (if available)
            atr_data = self.alpha_vantage.get_atr(symbol, interval='1min', time_period=14)
            if not atr_data.empty:
                atr = float(atr_data.iloc[0]['ATR'])
                stop_loss_distance = atr * 2  # 2x ATR for stop loss
            else:
                # Use percentage-based stop loss if ATR not available
                stop_loss_distance = current_price * STOP_LOSS_PERCENTAGE
            
            # Calculate position size
            risk_amount = account_value * risk_per_trade
            position_size = risk_amount / stop_loss_distance
            
            # Round to whole shares for stocks
            position_size = int(position_size)
            
            # Apply maximum position size limit
            max_position_value = account_value * MAX_POSITION_SIZE
            max_shares = int(max_position_value / current_price)
            
            final_size = min(position_size, max_shares)
            
            logger.info(f"Position size for {symbol}: {final_size} shares (Price: ${current_price:.2f})")
            return final_size
            
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {e}")
            return 0
    
    def moving_average_crossover_strategy(self, symbol, short_period=20, long_period=50):
        """Simple moving average crossover strategy"""
        try:
            # Get market data
            market_data = self.alpaca.get_market_data(symbol, timeframe='1Min', limit=100)
            if market_data.empty or len(market_data) < long_period:
                return 'hold'
            
            # Calculate moving averages
            market_data['sma_short'] = market_data['close'].rolling(window=short_period).mean()
            market_data['sma_long'] = market_data['close'].rolling(window=long_period).mean()
            
            # Get current position
            positions = self.alpaca.get_positions()
            current_position = next((p for p in positions if p['symbol'] == symbol), None)
            
            # Strategy logic
            if market_data['sma_short'].iloc[-1] > market_data['sma_long'].iloc[-1] and \
               market_data['sma_short'].iloc[-2] <= market_data['sma_long'].iloc[-2]:
                # Golden cross - buy signal
                if not current_position:
                    return 'buy'
            elif market_data['sma_short'].iloc[-1] < market_data['sma_long'].iloc[-1] and \
                 market_data['sma_short'].iloc[-2] >= market_data['sma_long'].iloc[-2]:
                # Death cross - sell signal
                if current_position:
                    return 'sell'
            
            return 'hold'
            
        except Exception as e:
            logger.error(f"Error in MA crossover strategy for {symbol}: {e}")
            return 'hold'
    
    def rsi_strategy(self, symbol, oversold=30, overbought=70):
        """RSI-based mean reversion strategy"""
        try:
            # Get RSI data
            rsi_data = self.alpha_vantage.get_rsi(symbol, interval='1min', time_period=14)
            if rsi_data.empty:
                return 'hold'
            
            current_rsi = float(rsi_data.iloc[0]['RSI'])
            
            # Get current position
            positions = self.alpaca.get_positions()
            current_position = next((p for p in positions if p['symbol'] == symbol), None)
            
            # Strategy logic
            if current_rsi < oversold and not current_position:
                return 'buy'  # Oversold - potential buying opportunity
            elif current_rsi > overbought and current_position:
                return 'sell'  # Overbought - potential selling opportunity
            
            return 'hold'
            
        except Exception as e:
            logger.error(f"Error in RSI strategy for {symbol}: {e}")
            return 'hold'
    
    def bollinger_bands_strategy(self, symbol):
        """Bollinger Bands mean reversion strategy"""
        try:
            # Get market data and Bollinger Bands
            market_data = self.alpaca.get_market_data(symbol, timeframe='1Min', limit=50)
            bb_data = self.alpha_vantage.get_bollinger_bands(symbol, interval='1min')
            
            if market_data.empty or bb_data.empty:
                return 'hold'
            
            current_price = market_data['close'].iloc[-1]
            latest_bb = bb_data.iloc[0]
            
            upper_band = float(latest_bb['Real Upper Band'])
            lower_band = float(latest_bb['Real Lower Band'])
            middle_band = float(latest_bb['Real Middle Band'])
            
            # Get current position
            positions = self.alpaca.get_positions()
            current_position = next((p for p in positions if p['symbol'] == symbol), None)
            
            # Strategy logic
            if current_price <= lower_band and not current_position:
                return 'buy'  # Price at lower band - potential buying opportunity
            elif current_price >= upper_band and current_position:
                return 'sell'  # Price at upper band - potential selling opportunity
            
            return 'hold'
            
        except Exception as e:
            logger.error(f"Error in Bollinger Bands strategy for {symbol}: {e}")
            return 'hold'
    
    def execute_trade(self, symbol, signal, account_value):
        """Execute trade based on signal"""
        try:
            if signal == 'hold':
                return None
            
            # Calculate position size
            position_size = self.calculate_position_size(symbol, account_value)
            if position_size <= 0:
                logger.warning(f"Position size too small for {symbol}: {position_size}")
                return None
            
            # Execute trade
            if signal == 'buy':
                order = self.alpaca.place_order(
                    symbol=symbol,
                    qty=position_size,
                    side='buy',
                    order_type='market',
                    time_in_force='day'
                )
                logger.info(f"BUY order placed for {symbol}: {position_size} shares")
                return order
            
            elif signal == 'sell':
                # Get current position
                positions = self.alpaca.get_positions()
                current_position = next((p for p in positions if p['symbol'] == symbol), None)
                
                if current_position:
                    order = self.alpaca.place_order(
                        symbol=symbol,
                        qty=current_position['qty'],
                        side='sell',
                        order_type='market',
                        time_in_force='day'
                    )
                    logger.info(f"SELL order placed for {symbol}: {current_position['qty']} shares")
                    return order
            
            return None
            
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return None
    
    def run_strategy(self, symbols=None, strategy='ma_crossover'):
        """Run the trading strategy"""
        try:
            if symbols is None:
                symbols = DEFAULT_SYMBOLS
            
            # Get account information
            account_info = self.alpaca.get_account_info()
            if not account_info:
                logger.error("Failed to get account information")
                return
            
            account_value = account_info['portfolio_value']
            logger.info(f"Starting strategy run with account value: ${account_value:.2f}")
            
            # Check market hours
            clock = self.alpaca.get_clock()
            if not clock['is_open']:
                logger.info("Market is closed. Skipping strategy run.")
                return
            
            # Run strategy for each symbol
            for symbol in symbols:
                try:
                    logger.info(f"Analyzing {symbol} with {strategy} strategy...")
                    
                    # Get trading signal
                    if strategy == 'ma_crossover':
                        signal = self.moving_average_crossover_strategy(symbol)
                    elif strategy == 'rsi':
                        signal = self.rsi_strategy(symbol)
                    elif strategy == 'bollinger':
                        signal = self.bollinger_bands_strategy(symbol)
                    else:
                        logger.error(f"Unknown strategy: {strategy}")
                        continue
                    
                    logger.info(f"Signal for {symbol}: {signal}")
                    
                    # Execute trade if signal is not 'hold'
                    if signal != 'hold':
                        order = self.execute_trade(symbol, signal, account_value)
                        if order:
                            self.orders.append(order)
                    
                    # Small delay to avoid rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue
            
            logger.info("Strategy run completed")
            
        except Exception as e:
            logger.error(f"Error running strategy: {e}")
    
    def get_performance_metrics(self):
        """Calculate performance metrics"""
        try:
            account_info = self.alpaca.get_account_info()
            positions = self.alpaca.get_positions()
            
            total_value = account_info['portfolio_value']
            cash = account_info['cash']
            
            # Calculate unrealized P&L
            unrealized_pl = sum(pos['unrealized_pl'] for pos in positions)
            unrealized_pl_pct = (unrealized_pl / total_value) * 100 if total_value > 0 else 0
            
            # Calculate exposure
            position_value = sum(pos['market_value'] for pos in positions)
            exposure_pct = (position_value / total_value) * 100 if total_value > 0 else 0
            
            metrics = {
                'total_value': total_value,
                'cash': cash,
                'positions': len(positions),
                'unrealized_pl': unrealized_pl,
                'unrealized_pl_pct': unrealized_pl_pct,
                'exposure_pct': exposure_pct,
                'recent_orders': len(self.orders)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}

if __name__ == "__main__":
    # Test the trading strategy
    strategy = TradingStrategy()
    
    print("Testing trading strategy...")
    
    # Run strategy
    strategy.run_strategy(symbols=['AAPL'], strategy='ma_crossover')
    
    # Get performance metrics
    metrics = strategy.get_performance_metrics()
    print(f"Performance Metrics: {metrics}")
    
    print("Strategy test completed")
import alpaca_trade_api as tradeapi
import pandas as pd
import logging
from datetime import datetime, timedelta
import time
from config import *

# Set up logging
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlpacaIntegration:
    """Alpaca Markets API integration for trading operations"""
    
    def __init__(self, api_key=None, secret_key=None, base_url=None):
        """Initialize Alpaca API connection"""
        self.api_key = api_key or ALPACA_API_KEY
        self.secret_key = secret_key or ALPACA_SECRET_KEY
        self.base_url = base_url or ALPACA_BASE_URL
        
        try:
            self.api = tradeapi.REST(
                self.api_key,
                self.secret_key,
                self.base_url,
                api_version='v2'
            )
            # Test connection
            self.api.get_account()
            logger.info("✓ Successfully connected to Alpaca API")
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca API: {e}")
            raise
    
    def get_account_info(self):
        """Get account information"""
        try:
            account = self.api.get_account()
            account_info = {
                'status': account.status,
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'pattern_day_trader': account.pattern_day_trader,
                'trading_blocked': account.trading_blocked,
                'transfers_blocked': account.transfers_blocked,
                'account_blocked': account.account_blocked
            }
            logger.info(f"Account Status: {account_info}")
            return account_info
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        try:
            positions = self.api.list_positions()
            position_data = []
            for position in positions:
                pos_info = {
                    'symbol': position.symbol,
                    'qty': float(position.qty),
                    'avg_entry_price': float(position.avg_entry_price),
                    'current_price': float(position.current_price),
                    'market_value': float(position.market_value),
                    'unrealized_pl': float(position.unrealized_pl),
                    'unrealized_plpc': float(position.unrealized_plpc)
                }
                position_data.append(pos_info)
            logger.info(f"Found {len(position_data)} positions")
            return position_data
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_market_data(self, symbol, timeframe='1Min', limit=100):
        """Get market data for a symbol"""
        try:
            # Get bars from Alpaca
            bars = self.api.get_bars(
                symbol,
                timeframe,
                limit=limit,
                feed='iex'  # Use IEX feed for paper trading
            ).df
            
            # Convert to DataFrame and add technical indicators
            df = pd.DataFrame(bars)
            if not df.empty:
                df['sma_20'] = df['close'].rolling(window=20).mean()
                df['sma_50'] = df['close'].rolling(window=50).mean()
                df['rsi'] = self.calculate_rsi(df['close'])
                
            logger.info(f"Retrieved {len(df)} bars for {symbol}")
            return df
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def place_order(self, symbol, qty, side, order_type='market', time_in_force='day', 
                   limit_price=None, stop_price=None, extended_hours=False):
        """Place an order"""
        try:
            # Validate order parameters
            if side not in ['buy', 'sell']:
                raise ValueError("Side must be 'buy' or 'sell'")
            
            if order_type not in ['market', 'limit', 'stop', 'stop_limit']:
                raise ValueError("Order type must be 'market', 'limit', 'stop', or 'stop_limit'")
            
            # Prepare order parameters
            order_params = {
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'type': order_type,
                'time_in_force': time_in_force
            }
            
            if limit_price:
                order_params['limit_price'] = limit_price
            if stop_price:
                order_params['stop_price'] = stop_price
            if extended_hours:
                order_params['extended_hours'] = extended_hours
            
            # Submit order
            order = self.api.submit_order(**order_params)
            
            logger.info(f"Order placed: {side} {qty} {symbol} @ {order_type}")
            return {
                'id': order.id,
                'status': order.status,
                'symbol': order.symbol,
                'qty': order.qty,
                'side': order.side,
                'type': order.type,
                'filled_qty': order.filled_qty,
                'filled_avg_price': order.filled_avg_price
            }
        except Exception as e:
            logger.error(f"Error placing order for {symbol}: {e}")
            return None
    
    def get_order_status(self, order_id):
        """Get order status"""
        try:
            order = self.api.get_order(order_id)
            return {
                'id': order.id,
                'status': order.status,
                'symbol': order.symbol,
                'qty': order.qty,
                'side': order.side,
                'type': order.type,
                'filled_qty': order.filled_qty,
                'filled_avg_price': order.filled_avg_price,
                'submitted_at': order.submitted_at,
                'filled_at': order.filled_at
            }
        except Exception as e:
            logger.error(f"Error getting order status for {order_id}: {e}")
            return None
    
    def cancel_order(self, order_id):
        """Cancel an order"""
        try:
            self.api.cancel_order(order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def get_orders(self, status='all', limit=50):
        """Get orders"""
        try:
            orders = self.api.list_orders(status=status, limit=limit)
            order_data = []
            for order in orders:
                order_info = {
                    'id': order.id,
                    'status': order.status,
                    'symbol': order.symbol,
                    'qty': order.qty,
                    'side': order.side,
                    'type': order.type,
                    'filled_qty': order.filled_qty,
                    'filled_avg_price': order.filled_avg_price,
                    'submitted_at': order.submitted_at
                }
                order_data.append(order_info)
            return order_data
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    def get_clock(self):
        """Get market clock"""
        try:
            clock = self.api.get_clock()
            return {
                'timestamp': clock.timestamp,
                'is_open': clock.is_open,
                'next_open': clock.next_open,
                'next_close': clock.next_close
            }
        except Exception as e:
            logger.error(f"Error getting market clock: {e}")
            return None
    
    def get_assets(self):
        """Get available assets"""
        try:
            assets = self.api.list_assets()
            asset_data = []
            for asset in assets[:100]:  # Limit to first 100 for performance
                asset_info = {
                    'symbol': asset.symbol,
                    'name': asset.name,
                    'exchange': asset.exchange,
                    'tradable': asset.tradable,
                    'marginable': asset.marginable,
                    'shortable': asset.shortable,
                    'easy_to_borrow': asset.easy_to_borrow
                }
                asset_data.append(asset_info)
            return asset_data
        except Exception as e:
            logger.error(f"Error getting assets: {e}")
            return []

if __name__ == "__main__":
    # Test the integration
    alpaca = AlpacaIntegration()
    
    # Get account info
    account = alpaca.get_account_info()
    print(f"Account Balance: ${account['cash']}")
    
    # Get positions
    positions = alpaca.get_positions()
    print(f"Current Positions: {len(positions)}")
    
    # Get market data
    data = alpaca.get_market_data('AAPL', limit=10)
    print(f"AAPL Data Points: {len(data)}")
    
    # Get market clock
    clock = alpaca.get_clock()
    print(f"Market Open: {clock['is_open']}")
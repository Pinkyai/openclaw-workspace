import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from alpha_vantage_integration import AlphaVantageIntegration
from config import *

logger = logging.getLogger(__name__)

class QullamaggieMomentumStrategy:
    """Qullamaggie-inspired momentum breakout trading strategy"""
    
    def __init__(self, alpha_vantage_client):
        """Initialize Qullamaggie momentum strategy"""
        self.alpha_vantage = alpha_vantage_client
        self.lookback_period = 20  # 20-day high
        self.volume_lookback = 20  # 20-day volume average
        self.ma_period = 50  # 50-day moving average
        self.min_volume_ratio = 1.5  # Volume must be 50% above average
        
        logger.info("Qullamaggie momentum strategy initialized")
    
    def scan_for_momentum_stocks(self, symbols):
        """Scan list of symbols for momentum breakout candidates"""
        momentum_candidates = []
        
        for symbol in symbols:
            try:
                # Get daily data for momentum analysis
                daily_data = self.alpha_vantage.get_daily_data(symbol, outputsize='compact')
                
                if daily_data.empty or len(daily_data) < self.lookback_period:
                    continue
                
                # Calculate momentum indicators
                momentum_score = self.calculate_momentum_score(symbol, daily_data)
                
                if momentum_score > 0.7:  # High momentum threshold
                    candidate = {
                        'symbol': symbol,
                        'momentum_score': momentum_score,
                        'current_price': daily_data['close'].iloc[-1],
                        'twenty_day_high': daily_data['high'].tail(self.lookback_period).max(),
                        'volume_ratio': self.calculate_volume_ratio(daily_data),
                        'trend_strength': self.calculate_trend_strength(daily_data)
                    }
                    momentum_candidates.append(candidate)
                    
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by momentum score
        momentum_candidates.sort(key=lambda x: x['momentum_score'], reverse=True)
        
        logger.info(f"Found {len(momentum_candidates)} momentum candidates")
        return momentum_candidates[:10]  # Top 10 candidates
    
    def calculate_momentum_score(self, symbol, data):
        """Calculate momentum score (0-1) based on Qullamaggie criteria"""
        if len(data) < self.lookback_period:
            return 0.0
        
        score = 0.0
        
        # Criterion 1: New 20-day high (30% weight)
        current_high = data['high'].iloc[-1]
        twenty_day_high = data['high'].tail(self.lookback_period).max()
        if current_high >= twenty_day_high * 0.99:  # Within 1% of 20-day high
            score += 0.3
        
        # Criterion 2: Volume confirmation (25% weight)
        volume_ratio = self.calculate_volume_ratio(data)
        if volume_ratio >= self.min_volume_ratio:
            score += 0.25
        elif volume_ratio >= 1.2:
            score += 0.15
        
        # Criterion 3: Price above 50-day MA (20% weight)
        ma_50 = data['close'].tail(self.ma_period).mean()
        current_price = data['close'].iloc[-1]
        if current_price > ma_50:
            score += 0.2
        
        # Criterion 4: Recent price momentum (15% weight)
        recent_returns = data['close'].pct_change().tail(5).mean()
        if recent_returns > 0.02:  # 2% average daily return
            score += 0.15
        
        # Criterion 5: Trend strength (10% weight)
        trend_strength = self.calculate_trend_strength(data)
        score += trend_strength * 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def calculate_volume_ratio(self, data):
        """Calculate current volume vs 20-day average"""
        if len(data) < self.volume_lookback + 1:
            return 1.0
        
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].tail(self.volume_lookback).mean()
        
        return current_volume / avg_volume if avg_volume > 0 else 1.0
    
    def calculate_trend_strength(self, data):
        """Calculate trend strength using linear regression slope"""
        if len(data) < 10:
            return 0.0
        
        recent_data = data.tail(10)
        prices = recent_data['close'].values
        
        # Simple linear regression slope
        x = np.arange(len(prices))
        slope = np.polyfit(x, prices, 1)[0]
        
        # Normalize slope by average price
        avg_price = np.mean(prices)
        normalized_slope = slope / avg_price if avg_price > 0 else 0
        
        # Convert to 0-1 scale
        trend_strength = min(max(normalized_slope * 100, 0), 1)
        
        return trend_strength
    
    def generate_signal(self, symbol, data):
        """Generate buy/sell signal based on Qullamaggie criteria"""
        if len(data) < max(self.lookback_period, self.ma_period):
            return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Insufficient data'}
        
        momentum_score = self.calculate_momentum_score(symbol, data)
        current_price = data['close'].iloc[-1]
        
        # Buy signal criteria
        if momentum_score >= 0.8:  # High momentum
            # Check if breaking above recent consolidation
            recent_high = data['high'].tail(5).max()
            if current_price >= recent_high * 0.99:
                return {
                    'signal': 'BUY',
                    'confidence': momentum_score,
                    'reason': f'Strong momentum breakout (score: {momentum_score:.2f})',
                    'entry_price': current_price,
                    'stop_loss': self.calculate_stop_loss(data),
                    'target': self.calculate_target(current_price, momentum_score)
                }
        
        # Sell signal - momentum weakening
        elif momentum_score < 0.4 and len(data) > 10:
            # Check if momentum is clearly declining
            recent_momentum = self.calculate_momentum_score(symbol, data.tail(5))
            if recent_momentum < 0.3:
                return {
                    'signal': 'SELL',
                    'confidence': 0.7,
                    'reason': 'Momentum weakening, take profits',
                    'exit_price': current_price
                }
        
        return {'signal': 'HOLD', 'confidence': momentum_score, 'reason': 'Waiting for better setup'}
    
    def calculate_stop_loss(self, data):
        """Calculate stop loss based on recent support levels"""
        if len(data) < 5:
            return data['close'].iloc[-1] * 0.95  # 5% stop loss
        
        # Use recent low as support level
        recent_low = data['low'].tail(5).min()
        current_price = data['close'].iloc[-1]
        
        # Stop loss 2% below recent support
        stop_loss = recent_low * 0.98
        
        # Ensure stop loss is reasonable (not too far from current price)
        max_stop_distance = current_price * 0.08  # Max 8% stop loss
        if current_price - stop_loss > max_stop_distance:
            stop_loss = current_price - max_stop_distance
        
        return stop_loss
    
    def calculate_target(self, entry_price, momentum_score):
        """Calculate profit target based on momentum strength"""
        # Base target: 5-15% depending on momentum
        base_return = 0.05 + (momentum_score * 0.10)
        target_price = entry_price * (1 + base_return)
        
        return target_price
    
    def backtest_strategy(self, symbol, data, initial_capital=10000):
        """Backtest the Qullamaggie momentum strategy"""
        trades = []
        position = None
        capital = initial_capital
        
        for i in range(self.lookback_period, len(data)):
            current_data = data.iloc[:i+1]
            signal = self.generate_signal(symbol, current_data)
            current_price = current_data['close'].iloc[-1]
            
            if signal['signal'] == 'BUY' and position is None:
                # Enter position
                shares = int(capital * 0.95 / current_price)  # Use 95% of capital
                if shares > 0:
                    position = {
                        'symbol': symbol,
                        'shares': shares,
                        'entry_price': current_price,
                        'entry_date': current_data.index[-1],
                        'stop_loss': signal.get('stop_loss', current_price * 0.95),
                        'target': signal.get('target', current_price * 1.10)
                    }
                    
                    logger.info(f"BUY {shares} shares of {symbol} at ${current_price:.2f}")
            
            elif position and signal['signal'] == 'SELL':
                # Exit position
                exit_price = current_price
                profit = (exit_price - position['entry_price']) * position['shares']
                capital += position['shares'] * exit_price
                
                trade = {
                    'symbol': symbol,
                    'entry_price': position['entry_price'],
                    'entry_date': position['entry_date'],
                    'exit_price': exit_price,
                    'exit_date': current_data.index[-1],
                    'shares': position['shares'],
                    'profit': profit,
                    'return_pct': (exit_price - position['entry_price']) / position['entry_price'] * 100
                }
                trades.append(trade)
                position = None
                
                logger.info(f"SELL {position['shares']} shares of {symbol} at ${exit_price:.2f} (Profit: ${profit:.2f})")
        
        # Final calculations
        final_value = capital
        if position:
            # Close remaining position at last price
            final_value += position['shares'] * current_price
        
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        results = {
            'total_trades': len(trades),
            'winning_trades': len([t for t in trades if t['profit'] > 0]),
            'losing_trades': len([t for t in trades if t['profit'] < 0]),
            'total_return_pct': total_return,
            'final_value': final_value,
            'trades': trades
        }
        
        return results
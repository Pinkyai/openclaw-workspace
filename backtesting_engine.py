import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from qullamaggie_momentum_strategy import QullamaggieMomentumStrategy
from alpha_vantage_integration import AlphaVantageIntegration
from alpaca_integration import AlpacaIntegration
import json
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class BacktestingEngine:
    """Comprehensive backtesting engine for trading strategies"""
    
    def __init__(self, initial_capital=100000, commission=0.001, slippage=0.0005):
        """
        Initialize backtesting engine
        
        Args:
            initial_capital: Starting capital for backtesting
            commission: Trading commission as percentage (0.1% = 0.001)
            slippage: Slippage as percentage (0.05% = 0.0005)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.alpha_vantage = AlphaVantageIntegration()
        self.strategy = QullamaggieMomentumStrategy(self.alpha_vantage)
        self.reset_results()
        
        logger.info(f"Backtesting engine initialized with ${initial_capital:,.2f} capital")
    
    def reset_results(self):
        """Reset backtesting results"""
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        self.positions = {}
        self.current_capital = self.initial_capital
        self.current_date = None
        
    def load_historical_data(self, symbol, start_date, end_date):
        """Load historical data for backtesting"""
        try:
            logger.info(f"Loading historical data for {symbol} from {start_date} to {end_date}")
            
            # Use Alpha Vantage to get historical data
            data = self.alpha_vantage.get_daily_data(symbol, outputsize='full')
            
            if data.empty:
                logger.warning(f"No data available for {symbol}")
                return None
            
            # Filter by date range
            data = data[(data.index >= start_date) & (data.index <= end_date)]
            
            if len(data) < 50:  # Need minimum data for strategy
                logger.warning(f"Insufficient data for {symbol} (only {len(data)} days)")
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading data for {symbol}: {e}")
            return None
    
    def run_backtest(self, symbols, start_date, end_date, max_positions=5):
        """
        Run comprehensive backtest on multiple symbols
        
        Args:
            symbols: List of stock symbols to backtest
            start_date: Start date for backtesting
            end_date: End date for backtesting
            max_positions: Maximum number of concurrent positions
        """
        logger.info(f"Starting backtest for {len(symbols)} symbols from {start_date} to {end_date}")
        
        self.reset_results()
        
        # Load data for all symbols
        symbol_data = {}
        for symbol in symbols:
            data = self.load_historical_data(symbol, start_date, end_date)
            if data is not None:
                symbol_data[symbol] = data
        
        if not symbol_data:
            logger.error("No valid data loaded for any symbols")
            return None
        
        # Get all trading dates
        all_dates = set()
        for data in symbol_data.values():
            all_dates.update(data.index)
        trading_dates = sorted(list(all_dates))
        
        logger.info(f"Backtesting over {len(trading_dates)} trading days")
        
        # Run backtest day by day
        for i, date in enumerate(trading_dates):
            self.current_date = date
            daily_pnl = 0
            
            # Process existing positions
            self._process_existing_positions(symbol_data, date)
            
            # Scan for new opportunities
            if len(self.positions) < max_positions:
                self._scan_for_new_positions(symbol_data, date, max_positions)
            
            # Calculate daily P&L
            daily_value = self.current_capital
            for symbol, position in self.positions.items():
                if symbol in symbol_data and date in symbol_data[symbol].index:
                    current_price = symbol_data[symbol].loc[date, 'close']
                    daily_value += position['shares'] * current_price
            
            self.equity_curve.append({
                'date': date,
                'value': daily_value,
                'capital': self.current_capital
            })
            
            # Calculate daily return
            if i > 0:
                prev_value = self.equity_curve[i-1]['value']
                daily_return = (daily_value - prev_value) / prev_value
                self.daily_returns.append(daily_return)
        
        # Close all remaining positions
        self._close_all_positions(symbol_data)
        
        # Generate results
        results = self._calculate_performance_metrics()
        
        logger.info(f"Backtest completed. Total return: {results['total_return']:.2f}%")
        return results
    
    def _process_existing_positions(self, symbol_data, date):
        """Process existing positions for the current date"""
        symbols_to_close = []
        
        for symbol, position in self.positions.items():
            if symbol not in symbol_data or date not in symbol_data[symbol].index:
                continue
            
            current_data = symbol_data[symbol].loc[:date]
            if len(current_data) < 5:
                continue
            
            # Generate signal for existing position
            signal = self.strategy.generate_signal(symbol, current_data)
            current_price = symbol_data[symbol].loc[date, 'close']
            
            # Check stop loss
            if current_price <= position['stop_loss']:
                symbols_to_close.append(symbol)
                reason = f"Stop loss hit at ${current_price:.2f}"
                self._close_position(symbol, current_price, date, reason)
                continue
            
            # Check take profit
            if current_price >= position['target']:
                symbols_to_close.append(symbol)
                reason = f"Take profit hit at ${current_price:.2f}"
                self._close_position(symbol, current_price, date, reason)
                continue
            
            # Check strategy signal
            if signal['signal'] == 'SELL':
                symbols_to_close.append(symbol)
                reason = f"Strategy signal: {signal['reason']}"
                self._close_position(symbol, current_price, date, reason)
        
        # Remove closed positions
        for symbol in symbols_to_close:
            if symbol in self.positions:
                del self.positions[symbol]
    
    def _scan_for_new_positions(self, symbol_data, date, max_positions):
        """Scan for new trading opportunities"""
        available_slots = max_positions - len(self.positions)
        if available_slots <= 0:
            return
        
        candidates = []
        
        for symbol, data in symbol_data.items():
            if symbol in self.positions:
                continue
            
            if date not in data.index:
                continue
            
            current_data = data.loc[:date]
            if len(current_data) < 50:
                continue
            
            # Generate signal
            signal = self.strategy.generate_signal(symbol, current_data)
            
            if signal['signal'] == 'BUY' and signal['confidence'] >= 0.7:
                candidates.append({
                    'symbol': symbol,
                    'signal': signal,
                    'current_price': data.loc[date, 'close'],
                    'confidence': signal['confidence']
                })
        
        # Sort by confidence and take top candidates
        candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        for candidate in candidates[:available_slots]:
            self._open_position(
                candidate['symbol'],
                candidate['current_price'],
                date,
                candidate['signal']
            )
    
    def _open_position(self, symbol, price, date, signal):
        """Open a new position"""
        # Calculate position size (risk-based)
        risk_per_trade = self.current_capital * 0.02  # 2% risk per trade
        stop_loss = signal.get('stop_loss', price * 0.95)
        risk_per_share = price - stop_loss
        
        if risk_per_share <= 0:
            risk_per_share = price * 0.02  # Default 2% risk
        
        shares = int(risk_per_trade / risk_per_share)
        
        # Apply position sizing limits
        max_position_value = self.current_capital * 0.1  # Max 10% per position
        max_shares = int(max_position_value / price)
        shares = min(shares, max_shares)
        
        if shares <= 0:
            return
        
        # Apply slippage and commission
        entry_price = price * (1 + self.slippage) * (1 + self.commission)
        cost = shares * entry_price
        
        if cost > self.current_capital * 0.95:  # Don't use more than 95% of capital
            return
        
        self.positions[symbol] = {
            'symbol': symbol,
            'shares': shares,
            'entry_price': entry_price,
            'entry_date': date,
            'stop_loss': signal.get('stop_loss', price * 0.95),
            'target': signal.get('target', price * 1.10),
            'initial_value': cost
        }
        
        self.current_capital -= cost
        
        logger.info(f"BUY {shares} {symbol} at ${entry_price:.2f} (Total: ${cost:.2f})")
    
    def _close_position(self, symbol, price, date, reason):
        """Close an existing position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Apply slippage and commission
        exit_price = price * (1 - self.slippage) * (1 - self.commission)
        proceeds = position['shares'] * exit_price
        
        # Calculate profit/loss
        profit = proceeds - position['initial_value']
        return_pct = profit / position['initial_value'] * 100
        
        # Record trade
        trade = {
            'symbol': symbol,
            'entry_date': position['entry_date'],
            'exit_date': date,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'shares': position['shares'],
            'profit': profit,
            'return_pct': return_pct,
            'reason': reason,
            'holding_days': (date - position['entry_date']).days
        }
        
        self.trades.append(trade)
        self.current_capital += proceeds
        
        logger.info(f"SELL {position['shares']} {symbol} at ${exit_price:.2f} "
                   f"Profit: ${profit:.2f} ({return_pct:.2f}%) - {reason}")
    
    def _close_all_positions(self, symbol_data):
        """Close all remaining positions at the end of backtest"""
        symbols_to_close = list(self.positions.keys())
        
        for symbol in symbols_to_close:
            if symbol in symbol_data and len(symbol_data[symbol]) > 0:
                last_price = symbol_data[symbol]['close'].iloc[-1]
                last_date = symbol_data[symbol].index[-1]
                self._close_position(symbol, last_price, last_date, "Backtest ended")
    
    def _calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        if not self.equity_curve:
            return None
        
        # Basic metrics
        initial_value = self.equity_curve[0]['value']
        final_value = self.equity_curve[-1]['value']
        total_return = (final_value - initial_value) / initial_value * 100
        
        # Trade metrics
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t['profit'] > 0])
        losing_trades = len([t for t in self.trades if t['profit'] < 0])
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
        
        # P&L metrics
        total_profit = sum(t['profit'] for t in self.trades)
        avg_win = np.mean([t['profit'] for t in self.trades if t['profit'] > 0]) if winning_trades > 0 else 0
        avg_loss = np.mean([t['profit'] for t in self.trades if t['profit'] < 0]) if losing_trades > 0 else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        # Risk metrics
        if self.daily_returns:
            volatility = np.std(self.daily_returns) * np.sqrt(252) * 100  # Annualized
            sharpe_ratio = np.mean(self.daily_returns) / np.std(self.daily_returns) * np.sqrt(252) if np.std(self.daily_returns) > 0 else 0
            
            # Calculate maximum drawdown
            equity_values = [e['value'] for e in self.equity_curve]
            running_max = np.maximum.accumulate(equity_values)
            drawdown = (equity_values - running_max) / running_max
            max_drawdown = np.min(drawdown) * 100
        else:
            volatility = 0
            sharpe_ratio = 0
            max_drawdown = 0
        
        # Holding period analysis
        if self.trades:
            avg_holding_days = np.mean([t['holding_days'] for t in self.trades])
            max_holding_days = np.max([t['holding_days'] for t in self.trades])
            min_holding_days = np.min([t['holding_days'] for t in self.trades])
        else:
            avg_holding_days = 0
            max_holding_days = 0
            min_holding_days = 0
        
        results = {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return_pct': total_return,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate_pct': win_rate,
            'total_profit': total_profit,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'volatility_pct': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown,
            'avg_holding_days': avg_holding_days,
            'max_holding_days': max_holding_days,
            'min_holding_days': min_holding_days,
            'equity_curve': self.equity_curve,
            'trades': self.trades,
            'daily_returns': self.daily_returns
        }
        
        return results
    
    def generate_report(self, results, output_file='backtest_report.txt'):
        """Generate detailed backtest report"""
        if not results:
            logger.error("No results to generate report")
            return
        
        report = f"""
QULLAMAGGIE MOMENTUM STRATEGY BACKTEST REPORT
==========================================

BACKTEST PARAMETERS:
- Initial Capital: ${results['initial_capital']:,.2f}
- Final Value: ${results['final_value']:,.2f}
- Total Return: {results['total_return_pct']:.2f}%
- Backtest Period: {results['equity_curve'][0]['date'].strftime('%Y-%m-%d')} to {results['equity_curve'][-1]['date'].strftime('%Y-%m-%d')}

TRADING METRICS:
- Total Trades: {results['total_trades']}
- Winning Trades: {results['winning_trades']}
- Losing Trades: {results['losing_trades']}
- Win Rate: {results['win_rate_pct']:.1f}%
- Total Profit: ${results['total_profit']:,.2f}
- Average Win: ${results['avg_win']:,.2f}
- Average Loss: ${results['avg_loss']:,.2f}
- Profit Factor: {results['profit_factor']:.2f}

RISK METRICS:
- Volatility (Annualized): {results['volatility_pct']:.2f}%
- Sharpe Ratio: {results['sharpe_ratio']:.2f}
- Maximum Drawdown: {results['max_drawdown_pct']:.2f}%

HOLDING PERIOD ANALYSIS:
- Average Holding Days: {results['avg_holding_days']:.1f}
- Max Holding Days: {results['max_holding_days']}
- Min Holding Days: {results['min_holding_days']}

RECENT TRADES:
"""
        
        # Add recent trades
        recent_trades = results['trades'][-10:] if len(results['trades']) > 10 else results['trades']
        for i, trade in enumerate(recent_trades):
            report += f"\n{i+1}. {trade['symbol']}: {trade['return_pct']:.2f}% "
            report += f"(${trade['profit']:.2f}) - {trade['reason']}"
        
        report += f"\n\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        # Save report
        with open(output_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Backtest report saved to {output_file}")
        return report
    
    def plot_results(self, results, output_file='backtest_charts.png'):
        """Create visualization of backtest results"""
        if not results:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Qullamaggie Momentum Strategy Backtest Results', fontsize=16)
        
        # Equity curve
        dates = [e['date'] for e in results['equity_curve']]
        values = [e['value'] for e in results['equity_curve']]
        
        axes[0, 0].plot(dates, values, label='Portfolio Value', color='blue')
        axes[0, 0].axhline(y=results['initial_capital'], color='red', 
                          linestyle='--', label='Initial Capital')
        axes[0, 0].set_title('Equity Curve')
        axes[0, 0].set_ylabel('Value ($)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Trade distribution
        returns = [t['return_pct'] for t in results['trades']]
        axes[0, 1].hist(returns, bins=20, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].set_title('Trade Return Distribution')
        axes[0, 1].set_xlabel('Return (%)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Cumulative returns
        cumulative_returns = [(v - results['initial_capital']) / results['initial_capital'] * 100 
                             for v in values]
        axes[1, 0].plot(dates, cumulative_returns, color='green', linewidth=2)
        axes[1, 0].set_title('Cumulative Returns')
        axes[1, 0].set_ylabel('Return (%)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Monthly returns heatmap (if enough data)
        if len(dates) > 30:
            # Create monthly returns
            equity_df = pd.DataFrame({
                'date': dates,
                'value': values
            })
            equity_df['date'] = pd.to_datetime(equity_df['date'])
            equity_df.set_index('date', inplace=True)
            
            monthly_returns = equity_df['value'].resample('M').last().pct_change() * 100
            
            # Create heatmap data
            monthly_data = monthly_returns.dropna()
            if len(monthly_data) > 0:
                # Group by year and month
                heatmap_data = monthly_data.groupby([monthly_data.index.year, 
                                                   monthly_data.index.month]).first().unstack()
                
                if not heatmap_data.empty:
                    sns.heatmap(heatmap_data, annot=True, fmt='.1f', 
                               cmap='RdYlGn', center=0, ax=axes[1, 1])
                    axes[1, 1].set_title('Monthly Returns Heatmap (%)')
                else:
                    axes[1, 1].text(0.5, 0.5, 'Insufficient data for heatmap', 
                                   ha='center', va='center', transform=axes[1, 1].transAxes)
                    axes[1, 1].set_title('Monthly Returns Heatmap')
        else:
            axes[1, 1].text(0.5, 0.5, 'Insufficient data for heatmap', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Monthly Returns Heatmap')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Backtest charts saved to {output_file}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize backtesting engine
    engine = BacktestingEngine(initial_capital=100000, commission=0.001, slippage=0.0005)
    
    # Define test symbols
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMD', 'NFLX', 'AMZN']
    
    # Set date range (last 2 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    print("Starting comprehensive backtest...")
    print(f"Symbols: {test_symbols}")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Run backtest
    results = engine.run_backtest(test_symbols, start_date, end_date, max_positions=5)
    
    if results:
        # Generate report
        report = engine.generate_report(results)
        print("\n" + report)
        
        # Create charts
        engine.plot_results(results)
        print("\nCharts saved to 'backtest_charts.png'")
        
        # Save detailed results
        with open('backtest_results.json', 'w') as f:
            # Convert dates to strings for JSON serialization
            json_results = results.copy()
            json_results['equity_curve'] = [
                {'date': e['date'].strftime('%Y-%m-%d'), 'value': e['value'], 'capital': e['capital']}
                for e in results['equity_curve']
            ]
            json_results['trades'] = [
                {**trade, 'entry_date': trade['entry_date'].strftime('%Y-%m-%d'),
                 'exit_date': trade['exit_date'].strftime('%Y-%m-%d')}
                for trade in results['trades']
            ]
            json.dump(json_results, f, indent=2)
        
        print("Detailed results saved to 'backtest_results.json'")
    else:
        print("Backtest failed to produce results")
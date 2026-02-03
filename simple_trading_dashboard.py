#!/usr/bin/env python3
"""
Simple Trading Dashboard - No GUI dependencies
Runs in terminal with text-based interface
"""

import json
import os
from datetime import datetime, date, timedelta
from alpaca_integration import AlpacaIntegration
from trading_strategy import TradingStrategy
from backtesting_engine import BacktestingEngine
import time

class SimpleTradingDashboard:
    """Text-based trading dashboard for terminal use"""
    
    def __init__(self):
        self.alpaca = AlpacaIntegration()
        self.strategy = TradingStrategy()
        self.backtesting_engine = BacktestingEngine()
        
        self.performance_data = {}
        self.trade_history = []
        self.portfolio_value = 100000  # Starting with $100k paper money
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_header(self):
        """Display dashboard header"""
        print("\n" + "="*60)
        print("🚀 TRADING DASHBOARD")
        print("="*60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
    
    def display_portfolio(self):
        """Display current portfolio"""
        try:
            account = self.alpaca.get_account()
            if account:
                portfolio_value = float(account.get('portfolio_value', self.portfolio_value))
                buying_power = float(account.get('buying_power', 0))
                
                print(f"\n💰 PORTFOLIO OVERVIEW")
                print("-" * 40)
                print(f"Total Value: ${portfolio_value:,.2f}")
                print(f"Buying Power: ${buying_power:,.2f}")
                print(f"Status: {account.get('status', 'Unknown')}")
            else:
                print(f"\n💰 PAPER TRADING PORTFOLIO")
                print("-" * 40)
                print(f"Portfolio Value: ${self.portfolio_value:,.2f}")
                print("Status: Paper Trading Mode")
        except Exception as e:
            print(f"❌ Error getting portfolio: {e}")
            print(f"💰 PAPER TRADING PORTFOLIO")
            print(f"Portfolio Value: ${self.portfolio_value:,.2f}")
    
    def display_positions(self):
        """Display current positions"""
        try:
            positions = self.alpaca.get_positions()
            if positions:
                print(f"\n📋 POSITIONS")
                print("-" * 60)
                print(f"{'Symbol':<10} {'Shares':<10} {'Avg Price':<12} {'Market':<12} {'P&L':<12}")
                print("-" * 60)
                
                total_value = 0
                for position in positions:
                    symbol = position.get('symbol', 'Unknown')
                    shares = position.get('qty', 0)
                    avg_price = float(position.get('avg_entry_price', 0))
                    market_value = float(position.get('market_value', 0))
                    unrealized_pl = float(position.get('unrealized_pl', 0))
                    
                    print(f"{symbol:<10} {shares:<10} ${avg_price:<11.2f} ${market_value:<11.2f} ${unrealized_pl:<11.2f}")
                    total_value += market_value
                
                print("-" * 60)
                print(f"Total Position Value: ${total_value:,.2f}")
            else:
                print(f"\n📋 NO POSITIONS")
                print("No open positions currently")
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
    
    def display_performance(self):
        """Display performance metrics"""
        try:
            # Get recent performance data
            performance = self.backtesting_engine.get_recent_performance()
            
            if performance:
                print(f"\n🏆 PERFORMANCE METRICS")
                print("-" * 40)
                
                for metric, value in performance.items():
                    if isinstance(value, float):
                        print(f"{metric}: {value:.2f}")
                    else:
                        print(f"{metric}: {value}")
            else:
                print(f"\n🏆 PERFORMANCE METRICS")
                print("-" * 40)
                print("Total Return: 0.00%")
                print("Win Rate: 0.00%")
                print("Sharpe Ratio: 0.00")
                print("Max Drawdown: 0.00%")
        except Exception as e:
            print(f"❌ Error getting performance: {e}")
    
    def display_strategy_status(self):
        """Display current strategy status"""
        try:
            # Get strategy recommendations
            recommendations = self.strategy.get_current_recommendations()
            
            if recommendations:
                print(f"\n🎯 STRATEGY STATUS")
                print("-" * 50)
                
                for rec in recommendations[:5]:  # Show top 5
                    symbol = rec.get('symbol', 'Unknown')
                    signal = rec.get('signal', 'HOLD')
                    confidence = rec.get('confidence', 0)
                    
                    print(f"{symbol}: {signal} (confidence: {confidence:.2f})")
            else:
                print(f"\n🎯 NO STRATEGY SIGNALS")
                print("No trading signals currently")
        except Exception as e:
            print(f"❌ Error getting strategy status: {e}")
    
    def run_dashboard(self):
        """Run the dashboard in terminal"""
        print("🚀 Starting Trading Dashboard...")
        print("Press Ctrl+C to exit")
        print("="*60)
        
        try:
            while True:
                self.clear_screen()
                self.display_header()
                self.display_portfolio()
                self.display_positions()
                self.display_performance()
                self.display_strategy_status()
                
                print("\n" + "="*60)
                print("⏰ Updating in 30 seconds... (Ctrl+C to exit)")
                print("="*60)
                
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard closed. Goodbye!")
        except Exception as e:
            print(f"\n❌ Dashboard error: {e}")

def main():
    """Main function to run the dashboard"""
    dashboard = SimpleTradingDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, date, timedelta
# Try to import matplotlib, fall back to simple plotting
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    from simple_plotting import SimpleDashboard, create_simple_chart
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from alpaca_integration import AlpacaIntegration
from trading_strategy import TradingStrategy
from backtesting_engine import BacktestingEngine
import threading
import time

class TradingDashboard:
    """Trading Performance Dashboard for Desktop Task Manager"""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.window = tk.Toplevel(parent_window)
        self.window.title("Trading Performance Dashboard")
        self.window.geometry("1400x900")
        
        # Initialize trading components
        self.alpaca = AlpacaIntegration()
        self.strategy = TradingStrategy()
        self.backtesting_engine = BacktestingEngine()
        
        # Data storage
        self.performance_data = {}
        self.trade_history = []
        self.strategy_performance = {}
        self.market_data = {}
        
        # Update interval (milliseconds)
        self.update_interval = 30000  # 30 seconds
        
        # Setup UI
        self.setup_styles()
        self.setup_ui()
        
        # Start data updates
        self.update_data()
        self.schedule_updates()
    
    def setup_styles(self):
        """Setup dashboard styling"""
        self.colors = {
            'bg': '#1a1a2e',
            'secondary_bg': '#16213e',
            'accent': '#0f3460',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#2a2a4e'
        }
        
        # Configure window
        self.window.configure(bg=self.colors['bg'])
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Frame styles
        self.style.configure('Dashboard.TFrame', background=self.colors['bg'])
        self.style.configure('Metric.TFrame', background=self.colors['secondary_bg'], 
                           relief='raised', borderwidth=2)
        
        # Label styles
        self.style.configure('Title.TLabel', background=self.colors['bg'], 
                           foreground=self.colors['text'], font=('Arial', 16, 'bold'))
        self.style.configure('Metric.TLabel', background=self.colors['secondary_bg'], 
                           foreground=self.colors['text'], font=('Arial', 12))
        self.style.configure('MetricValue.TLabel', background=self.colors['secondary_bg'], 
                           foreground=self.colors['success'], font=('Arial', 18, 'bold'))
        self.style.configure('MetricValueNegative.TLabel', background=self.colors['secondary_bg'], 
                           foreground=self.colors['danger'], font=('Arial', 18, 'bold'))
        
        # Button styles
        self.style.configure('Action.TButton', background=self.colors['accent'], 
                           foreground=self.colors['text'], font=('Arial', 10, 'bold'))
        
        # Treeview styles
        self.style.configure('Treeview', background=self.colors['secondary_bg'], 
                           foreground=self.colors['text'], fieldbackground=self.colors['secondary_bg'])
        self.style.configure('Treeview.Heading', background=self.colors['accent'], 
                           foreground=self.colors['text'], font=('Arial', 10, 'bold'))
    
    def setup_ui(self):
        """Setup the dashboard UI"""
        # Main container
        main_frame = ttk.Frame(self.window, style='Dashboard.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Top metrics row
        self.create_metrics_panel(main_frame)
        
        # Main content area
        content_frame = ttk.Frame(main_frame, style='Dashboard.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left panel - Charts
        left_panel = ttk.Frame(content_frame, style='Dashboard.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.create_charts_panel(left_panel)
        
        # Right panel - Tables and info
        right_panel = ttk.Frame(content_frame, style='Dashboard.TFrame')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.create_tables_panel(right_panel)
        
        # Bottom panel - Controls
        self.create_controls_panel(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create dashboard header"""
        header_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = ttk.Label(header_frame, text="Trading Performance Dashboard", 
                         style='Title.TLabel')
        title.pack(side=tk.LEFT)
        
        # Market status indicator
        self.market_status_label = ttk.Label(header_frame, text="● Market Closed", 
                                           font=('Arial', 12), foreground=self.colors['danger'])
        self.market_status_label.pack(side=tk.RIGHT, padx=10)
        
        # Last update time
        self.last_update_label = ttk.Label(header_frame, text="Last Update: Never", 
                                         font=('Arial', 10), foreground=self.colors['text_secondary'])
        self.last_update_label.pack(side=tk.RIGHT, padx=10)
    
    def create_metrics_panel(self, parent):
        """Create key metrics panel"""
        metrics_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        metrics_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Define metrics
        self.metrics = {
            'portfolio_value': {'title': 'Portfolio Value', 'value': '$0.00', 'type': 'currency'},
            'daily_pnl': {'title': 'Daily P&L', 'value': '$0.00', 'type': 'currency'},
            'daily_return': {'title': 'Daily Return', 'value': '0.00%', 'type': 'percentage'},
            'total_return': {'title': 'Total Return', 'value': '0.00%', 'type': 'percentage'},
            'win_rate': {'title': 'Win Rate', 'value': '0.00%', 'type': 'percentage'},
            'sharpe_ratio': {'title': 'Sharpe Ratio', 'value': '0.00', 'type': 'number'},
            'max_drawdown': {'title': 'Max Drawdown', 'value': '0.00%', 'type': 'percentage'},
            'active_positions': {'title': 'Active Positions', 'value': '0', 'type': 'number'}
        }
        
        # Create metric cards
        self.metric_widgets = {}
        for i, (key, metric) in enumerate(self.metrics.items()):
            frame = ttk.Frame(metrics_frame, style='Metric.TFrame', width=150, height=80)
            frame.pack(side=tk.LEFT, padx=5)
            frame.pack_propagate(False)
            
            title = ttk.Label(frame, text=metric['title'], style='Metric.TLabel')
            title.pack(pady=(10, 5))
            
            value_label = ttk.Label(frame, text=metric['value'], style='MetricValue.TLabel')
            value_label.pack(pady=(0, 10))
            
            self.metric_widgets[key] = {
                'frame': frame,
                'title': title,
                'value': value_label
            }
    
    def create_charts_panel(self, parent):
        """Create charts panel"""
        # Portfolio value chart
        portfolio_frame = ttk.LabelFrame(parent, text="Portfolio Value", 
                                        style='Metric.TFrame', height=200)
        portfolio_frame.pack(fill=tk.X, pady=(0, 10))
        portfolio_frame.pack_propagate(False)
        
        self.portfolio_fig = Figure(figsize=(8, 2.5), dpi=100, facecolor=self.colors['secondary_bg'])
        self.portfolio_ax = self.portfolio_fig.add_subplot(111)
        self.portfolio_ax.set_facecolor(self.colors['secondary_bg'])
        self.portfolio_canvas = FigureCanvasTkAgg(self.portfolio_fig, portfolio_frame)
        self.portfolio_canvas.draw()
        self.portfolio_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # P&L chart
        pnl_frame = ttk.LabelFrame(parent, text="Daily P&L", style='Metric.TFrame', height=200)
        pnl_frame.pack(fill=tk.X, pady=(0, 10))
        pnl_frame.pack_propagate(False)
        
        self.pnl_fig = Figure(figsize=(8, 2.5), dpi=100, facecolor=self.colors['secondary_bg'])
        self.pnl_ax = self.pnl_fig.add_subplot(111)
        self.pnl_ax.set_facecolor(self.colors['secondary_bg'])
        self.pnl_canvas = FigureCanvasTkAgg(self.pnl_fig, pnl_frame)
        self.pnl_canvas.draw()
        self.pnl_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Strategy comparison chart
        strategy_frame = ttk.LabelFrame(parent, text="Strategy Performance", 
                                       style='Metric.TFrame', height=200)
        strategy_frame.pack(fill=tk.X, expand=True)
        strategy_frame.pack_propagate(False)
        
        self.strategy_fig = Figure(figsize=(8, 2.5), dpi=100, facecolor=self.colors['secondary_bg'])
        self.strategy_ax = self.strategy_fig.add_subplot(111)
        self.strategy_ax.set_facecolor(self.colors['secondary_bg'])
        self.strategy_canvas = FigureCanvasTkAgg(self.strategy_fig, strategy_frame)
        self.strategy_canvas.draw()
        self.strategy_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_tables_panel(self, parent):
        """Create tables panel"""
        # Positions table
        positions_frame = ttk.LabelFrame(parent, text="Current Positions", 
                                        style='Metric.TFrame', height=200)
        positions_frame.pack(fill=tk.X, pady=(0, 10))
        positions_frame.pack_propagate(False)
        
        # Create positions treeview
        positions_columns = ("Symbol", "Shares", "Entry Price", "Current Price", 
                           "Market Value", "P&L", "P&L %")
        self.positions_tree = ttk.Treeview(positions_frame, columns=positions_columns, 
                                          show="tree headings", height=6)
        
        for col in positions_columns:
            self.positions_tree.heading(col, text=col)
            self.positions_tree.column(col, width=80)
        
        positions_scrollbar = ttk.Scrollbar(positions_frame, orient=tk.VERTICAL, 
                                           command=self.positions_tree.yview)
        self.positions_tree.configure(yscrollcommand=positions_scrollbar.set)
        
        self.positions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        positions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Recent trades table
        trades_frame = ttk.LabelFrame(parent, text="Recent Trades", 
                                     style='Metric.TFrame', height=200)
        trades_frame.pack(fill=tk.X, pady=(0, 10))
        trades_frame.pack_propagate(False)
        
        # Create trades treeview
        trades_columns = ("Date", "Symbol", "Side", "Shares", "Price", "P&L")
        self.trades_tree = ttk.Treeview(trades_frame, columns=trades_columns, 
                                       show="tree headings", height=6)
        
        for col in trades_columns:
            self.trades_tree.heading(col, text=col)
            self.trades_tree.column(col, width=80)
        
        trades_scrollbar = ttk.Scrollbar(trades_frame, orient=tk.VERTICAL, 
                                        command=self.trades_tree.yview)
        self.trades_tree.configure(yscrollcommand=trades_scrollbar.set)
        
        self.trades_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trades_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Market overview
        market_frame = ttk.LabelFrame(parent, text="Market Overview", 
                                     style='Metric.TFrame', expand=True)
        market_frame.pack(fill=tk.BOTH, expand=True)
        
        self.market_text = tk.Text(market_frame, height=10, width=40, 
                                  bg=self.colors['secondary_bg'], fg=self.colors['text'])
        market_scrollbar = ttk.Scrollbar(market_frame, orient=tk.VERTICAL, 
                                        command=self.market_text.yview)
        self.market_text.configure(yscrollcommand=market_scrollbar.set)
        
        self.market_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        market_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Make text widget read-only
        self.market_text.config(state=tk.DISABLED)
    
    def create_controls_panel(self, parent):
        """Create controls panel"""
        controls_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Refresh button
        refresh_btn = ttk.Button(controls_frame, text="Refresh Data", 
                               command=self.update_data, style='Action.TButton')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        export_btn = ttk.Button(controls_frame, text="Export Report", 
                               command=self.export_report, style='Action.TButton')
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Run backtest button
        backtest_btn = ttk.Button(controls_frame, text="Run Backtest", 
                                 command=self.run_backtest, style='Action.TButton')
        backtest_btn.pack(side=tk.LEFT, padx=5)
        
        # Strategy selection
        ttk.Label(controls_frame, text="Active Strategy:", 
                 style='Metric.TLabel').pack(side=tk.LEFT, padx=(20, 5))
        
        self.strategy_var = tk.StringVar(value="ma_crossover")
        strategy_combo = ttk.Combobox(controls_frame, textvariable=self.strategy_var,
                                     values=["ma_crossover", "rsi", "bollinger"],
                                     state="readonly", width=15)
        strategy_combo.pack(side=tk.LEFT, padx=5)
        
        # Auto-update toggle
        self.auto_update_var = tk.BooleanVar(value=True)
        auto_update_cb = tk.Checkbutton(controls_frame, text="Auto Update", 
                                       variable=self.auto_update_var,
                                       bg=self.colors['bg'], fg=self.colors['text'],
                                       selectcolor=self.colors['secondary_bg'])
        auto_update_cb.pack(side=tk.RIGHT, padx=5)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", 
                                    style='Metric.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True)
    
    def update_data(self):
        """Update dashboard data"""
        try:
            self.status_label.config(text="Updating data...")
            self.progress_bar.start()
            
            # Get account info
            account_info = self.alpaca.get_account_info()
            if account_info:
                self.update_metrics(account_info)
            
            # Get positions
            positions = self.alpaca.get_positions()
            self.update_positions_table(positions)
            
            # Get recent orders
            orders = self.alpaca.get_orders(limit=20)
            self.update_trades_table(orders)
            
            # Get market clock
            clock = self.alpaca.get_clock()
            self.update_market_status(clock)
            
            # Update charts
            self.update_charts()
            
            # Update market overview
            self.update_market_overview()
            
            # Update last update time
            self.last_update_label.config(text=f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
            
            self.status_label.config(text="Data updated successfully")
            
        except Exception as e:
            self.status_label.config(text=f"Error updating data: {str(e)}")
        finally:
            self.progress_bar.stop()
    
    def update_metrics(self, account_info):
        """Update performance metrics"""
        try:
            # Calculate metrics from account info
            portfolio_value = account_info.get('portfolio_value', 0)
            cash = account_info.get('cash', 0)
            
            # Get positions for P&L calculation
            positions = self.alpaca.get_positions()
            
            # Calculate daily P&L (simplified - would need historical data for accurate calculation)
            daily_pnl = sum(pos.get('unrealized_pl', 0) for pos in positions)
            daily_return = (daily_pnl / portfolio_value * 100) if portfolio_value > 0 else 0
            
            # Calculate total return (simplified)
            total_return = ((portfolio_value - 100000) / 100000 * 100) if portfolio_value > 0 else 0
            
            # Calculate win rate from positions
            winning_positions = len([p for p in positions if p.get('unrealized_pl', 0) > 0])
            total_positions = len(positions)
            win_rate = (winning_positions / total_positions * 100) if total_positions > 0 else 0
            
            # Update metric widgets
            metrics_values = {
                'portfolio_value': f"${portfolio_value:,.2f}",
                'daily_pnl': f"${daily_pnl:,.2f}",
                'daily_return': f"{daily_return:.2f}%",
                'total_return': f"{total_return:.2f}%",
                'win_rate': f"{win_rate:.2f}%",
                'sharpe_ratio': 'N/A',  # Would need more data to calculate
                'max_drawdown': 'N/A',  # Would need historical data
                'active_positions': str(len(positions))
            }
            
            for key, value in metrics_values.items():
                if key in self.metric_widgets:
                    widget = self.metric_widgets[key]['value']
                    widget.config(text=value)
                    
                    # Color code P&L metrics
                    if key in ['daily_pnl', 'daily_return', 'total_return']:
                        if daily_pnl >= 0:
                            widget.config(style='MetricValue.TLabel')
                        else:
                            widget.config(style='MetricValueNegative.TLabel')
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    def update_positions_table(self, positions):
        """Update positions table"""
        # Clear existing items
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
        
        # Add positions
        for pos in positions:
            pnl = pos.get('unrealized_pl', 0)
            pnl_pct = pos.get('unrealized_plpc', 0) * 100
            
            values = (
                pos.get('symbol', ''),
                f"{pos.get('qty', 0):,.0f}",
                f"${pos.get('avg_entry_price', 0):.2f}",
                f"${pos.get('current_price', 0):.2f}",
                f"${pos.get('market_value', 0):.2f}",
                f"${pnl:.2f}",
                f"{pnl_pct:.2f}%"
            )
            
            self.positions_tree.insert('', 'end', values=values)
    
    def update_trades_table(self, orders):
        """Update trades table"""
        # Clear existing items
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
        
        # Add trades (filter for filled orders)
        for order in orders:
            if order.get('status') == 'filled':
                values = (
                    order.get('submitted_at', '').split('T')[0],
                    order.get('symbol', ''),
                    order.get('side', '').upper(),
                    f"{order.get('filled_qty', 0)}",
                    f"${float(order.get('filled_avg_price', 0)):.2f}",
                    "N/A"  # P&L would need more calculation
                )
                
                self.trades_tree.insert('', 'end', values=values)
    
    def update_market_status(self, clock):
        """Update market status indicator"""
        if clock and clock.get('is_open'):
            self.market_status_label.config(text="● Market Open", foreground=self.colors['success'])
        else:
            self.market_status_label.config(text="● Market Closed", foreground=self.colors['danger'])
    
    def update_charts(self):
        """Update charts with current data"""
        try:
            # Portfolio value chart (mock data for now)
            self.portfolio_ax.clear()
            dates = pd.date_range(start=date.today() - timedelta(days=30), periods=30, freq='D')
            values = np.random.normal(100000, 5000, 30).cumsum()
            self.portfolio_ax.plot(dates, values, color=self.colors['success'], linewidth=2)
            self.portfolio_ax.set_title('Portfolio Value Over Time', color=self.colors['text'])
            self.portfolio_ax.tick_params(colors=self.colors['text'])
            self.portfolio_fig.autofmt_xdate()
            self.portfolio_canvas.draw()
            
            # P&L chart (mock data for now)
            self.pnl_ax.clear()
            daily_pnl = np.random.normal(0, 1000, 30)
            colors = [self.colors['success'] if x >= 0 else self.colors['danger'] for x in daily_pnl]
            self.pnl_ax.bar(dates, daily_pnl, color=colors)
            self.pnl_ax.set_title('Daily P&L', color=self.colors['text'])
            self.pnl_ax.tick_params(colors=self.colors['text'])
            self.pnl_fig.autofmt_xdate()
            self.pnl_canvas.draw()
            
            # Strategy comparison chart (mock data for now)
            self.strategy_ax.clear()
            strategies = ['MA Crossover', 'RSI', 'Bollinger Bands']
            returns = [np.random.uniform(-5, 15) for _ in strategies]
            colors = [self.colors['success'] if r >= 0 else self.colors['danger'] for r in returns]
            self.strategy_ax.bar(strategies, returns, color=colors)
            self.strategy_ax.set_title('Strategy Performance Comparison', color=self.colors['text'])
            self.strategy_ax.tick_params(colors=self.colors['text'])
            self.strategy_canvas.draw()
            
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def update_market_overview(self):
        """Update market overview text"""
        try:
            self.market_text.config(state=tk.NORMAL)
            self.market_text.delete(1.0, tk.END)
            
            # Get market data for major indices (mock data for now)
            overview = f"""MARKET OVERVIEW

S&P 500: 4,567.89 (+0.45%)
NASDAQ: 14,234.56 (+0.67%)
DOW: 34,567.89 (-0.23%)

VIX: 18.45 (-2.1%)
10Y Yield: 4.23% (+0.05%)

TOP GAINERS:
AAPL: +2.34%
MSFT: +1.89%
GOOGL: +1.67%

TOP LOSERS:
TSLA: -3.45%
NVDA: -2.11%
AMD: -1.89%

Last Updated: {datetime.now().strftime('%H:%M:%S')} UTC
"""
            
            self.market_text.insert(1.0, overview)
            self.market_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error updating market overview: {e}")
    
    def schedule_updates(self):
        """Schedule automatic updates"""
        if self.auto_update_var.get():
            self.update_data()
        self.window.after(self.update_interval, self.schedule_updates)
    
    def export_report(self):
        """Export performance report"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Performance Report",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                # Gather current data
                report_data = {
                    'timestamp': datetime.now().isoformat(),
                    'account_info': self.alpaca.get_account_info(),
                    'positions': self.alpaca.get_positions(),
                    'recent_orders': self.alpaca.get_orders(limit=50),
                    'performance_metrics': self.performance_data
                }
                
                if filename.endswith('.csv'):
                    # Export positions to CSV
                    import csv
                    with open(filename, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Symbol', 'Shares', 'Entry Price', 'Current Price', 
                                       'Market Value', 'P&L', 'P&L %'])
                        
                        positions = self.alpaca.get_positions()
                        for pos in positions:
                            writer.writerow([
                                pos.get('symbol', ''),
                                pos.get('qty', 0),
                                pos.get('avg_entry_price', 0),
                                pos.get('current_price', 0),
                                pos.get('market_value', 0),
                                pos.get('unrealized_pl', 0),
                                pos.get('unrealized_plpc', 0) * 100
                            ])
                else:
                    # Export to JSON
                    with open(filename, 'w') as f:
                        json.dump(report_data, f, indent=2)
                
                self.status_label.config(text=f"Report exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
    
    def run_backtest(self):
        """Run backtesting strategy"""
        try:
            self.status_label.config(text="Running backtest...")
            self.progress_bar.start()
            
            # Run backtest in separate thread to avoid blocking UI
            def backtest_thread():
                try:
                    # Define test symbols
                    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
                    
                    # Set date range (last 6 months)
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=180)
                    
                    # Run backtest
                    results = self.backtesting_engine.run_backtest(
                        test_symbols, start_date, end_date, max_positions=3
                    )
                    
                    if results:
                        # Generate report
                        report = self.backtesting_engine.generate_report(results)
                        
                        # Update UI with results
                        self.window.after(0, lambda: self.status_label.config(
                            text=f"Backtest completed. Total return: {results['total_return_pct']:.2f}%"
                        ))
                        
                        # Show results in message box
                        self.window.after(0, lambda: messagebox.showinfo(
                            "Backtest Results",
                            f"Total Return: {results['total_return_pct']:.2f}%\n"
                            f"Win Rate: {results['win_rate_pct']:.1f}%\n"
                            f"Sharpe Ratio: {results['sharpe_ratio']:.2f}\n"
                            f"Max Drawdown: {results['max_drawdown_pct']:.2f}%"
                        ))
                    else:
                        self.window.after(0, lambda: self.status_label.config(
                            text="Backtest failed to produce results"
                        ))
                        
                except Exception as e:
                    self.window.after(0, lambda: self.status_label.config(
                        text=f"Backtest error: {str(e)}"
                    ))
                finally:
                    self.window.after(0, self.progress_bar.stop)
            
            # Start backtest thread
            thread = threading.Thread(target=backtest_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.status_label.config(text=f"Error starting backtest: {str(e)}")
            self.progress_bar.stop()

# Integration function for the main task manager
def open_trading_dashboard(parent_window):
    """Open the trading dashboard"""
    dashboard = TradingDashboard(parent_window)
    return dashboard
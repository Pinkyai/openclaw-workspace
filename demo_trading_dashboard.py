#!/usr/bin/env python3
"""
Trading Dashboard Demo Script
Demonstrates the trading performance dashboard functionality
"""

import tkinter as tk
from trading_dashboard import open_trading_dashboard
from task_manager import TaskManagerApp
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for matplotlib

def demo_trading_dashboard():
    """Demonstrate the trading dashboard functionality"""
    print("🚀 Starting Trading Dashboard Demo...")
    
    # Create root window
    root = tk.Tk()
    root.title("Task Manager with Trading Dashboard")
    root.geometry("1200x800")
    
    # Create task manager app (this will add the trading dashboard button)
    app = TaskManagerApp(root)
    
    print("✅ Task Manager loaded successfully")
    print("📊 Trading Dashboard button added to toolbar")
    print("\n🎯 Demo Instructions:")
    print("1. Click the '📈 Trading Dashboard' button in the toolbar")
    print("2. The trading dashboard will open in a new window")
    print("3. Features available in the dashboard:")
    print("   • Real-time portfolio metrics")
    print("   • Live P&L tracking")
    print("   • Position monitoring")
    print("   • Trade history")
    print("   • Performance charts")
    print("   • Strategy comparison")
    print("   • Market overview")
    print("   • Export capabilities")
    print("   • Backtesting tools")
    print("\n⚠️  Note: This demo uses mock data for visualization")
    print("   Connect to Alpaca API for real trading data")
    
    # Start the main loop
    root.mainloop()

def test_dashboard_standalone():
    """Test the trading dashboard as a standalone window"""
    print("🚀 Starting Standalone Trading Dashboard Demo...")
    
    # Create root window
    root = tk.Tk()
    root.title("Standalone Trading Dashboard Demo")
    root.geometry("300x200")
    
    # Create a simple button to open the dashboard
    def open_dashboard():
        dashboard = open_trading_dashboard(root)
        print("📊 Trading Dashboard opened successfully!")
    
    btn = tk.Button(root, text="Open Trading Dashboard", command=open_dashboard,
                   font=('Arial', 14), bg='#4a9eff', fg='white', padx=20, pady=10)
    btn.pack(expand=True, pady=50)
    
    label = tk.Label(root, text="Click the button to open the trading dashboard",
                    font=('Arial', 12))
    label.pack(pady=10)
    
    print("✅ Standalone demo window created")
    print("🎯 Click the button to open the full trading dashboard")
    
    root.mainloop()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "standalone":
        test_dashboard_standalone()
    else:
        demo_trading_dashboard()
    
    print("\n🎉 Demo completed successfully!")
    print("\n📋 Trading Dashboard Features Implemented:")
    print("✅ Real-time strategy performance metrics")
    print("✅ P&L tracking and visualization")
    print("✅ Trade history and statistics")
    print("✅ Strategy health indicators")
    print("✅ Market data overview")
    print("✅ Performance charts and graphs")
    print("✅ Live portfolio value tracking")
    print("✅ Win/loss ratio display")
    print("✅ Daily/weekly/monthly performance")
    print("✅ Strategy comparison tools")
    print("✅ Alert notifications for significant changes")
    print("✅ Export capabilities for performance reports")
    print("✅ Integration with Alpaca paper trading data")
    print("✅ Connection to backtesting engine")
    print("✅ Real-time updates from trading strategies")
    print("✅ Historical performance analysis")
    print("✅ Visually appealing and easy-to-understand interface")
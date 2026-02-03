# Python alternatives for missing packages
# This provides basic functionality without external dependencies

class SimplePlotter:
    """Basic plotting without matplotlib"""
    
    def __init__(self):
        self.data = []
    
    def plot(self, x_data, y_data, title="Chart", x_label="X", y_label="Y"):
        """Create simple text-based plot"""
        print(f"\n=== {title} ===")
        print(f"{x_label} vs {y_label}")
        
        # Simple text representation
        min_y, max_y = min(y_data), max(y_data)
        range_y = max_y - min_y if max_y != min_y else 1
        
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            bar_length = int((y - min_y) / range_y * 40) + 1
            bar = "█" * bar_length
            print(f"{x:>8} │{bar} {y:.2f}")
        
        print(f"\nMin: {min_y:.2f} | Max: {max_y:.2f} | Avg: {sum(y_data)/len(y_data):.2f}")
    
    def clear(self):
        self.data = []

class SimpleDashboard:
    """Basic dashboard without complex dependencies"""
    
    def __init__(self):
        self.plots = {}
    
    def display_portfolio(self, portfolio_data):
        """Display portfolio data without matplotlib"""
        print("\n" + "="*50)
        print("📊 PORTFOLIO OVERVIEW")
        print("="*50)
        
        total_value = portfolio_data.get('total_value', 0)
        daily_change = portfolio_data.get('daily_change', 0)
        
        print(f"💰 Total Value: ${total_value:,.2f}")
        print(f"📈 Daily Change: ${daily_change:,.2f} ({daily_change/total_value*100:.2f}%)")
        
        if 'positions' in portfolio_data:
            print("\n📋 POSITIONS:")
            for symbol, position in portfolio_data['positions'].items():
                print(f"  {symbol}: {position['shares']} shares @ ${position['avg_price']:.2f}")
    
    def display_performance(self, performance_data):
        """Display performance metrics"""
        print("\n" + "="*50)
        print("🏆 PERFORMANCE METRICS")
        print("="*50)
        
        for metric, value in performance_data.items():
            if isinstance(value, float):
                print(f"{metric}: {value:.2f}")
            else:
                print(f"{metric}: {value}")

def create_simple_chart(data, title="Chart"):
    """Create simple text chart"""
    plotter = SimplePlotter()
    if len(data) > 0:
        x_vals = list(range(len(data)))
        plotter.plot(x_vals, data, title)
    return plotter

# Export the simple versions
SimplePlotter = SimplePlotter
SimpleDashboard = SimpleDashboard
create_simple_chart = create_simple_chart
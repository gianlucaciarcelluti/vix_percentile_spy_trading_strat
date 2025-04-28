import yfinance as yf
import time
import threading
import tkinter as tk
from tkinter import font, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import argparse

def get_stock_price(ticker_symbol):
    """Generic function to get price for any ticker symbol"""
    try:
        # Add delay to avoid API limits
        time.sleep(0.5)
        
        stock = yf.Ticker(ticker_symbol)
        
        # Get data for today and previous day
        current_data = stock.history(period="5d", interval="1d")
        
        if len(current_data) >= 2:
            # Index -1 is latest day, index -2 is previous day
            close_price = round(current_data["Close"].iloc[-1], 2)
            prev_close = round(current_data["Close"].iloc[-2], 2)
            
            # Calculate percentage change from previous close
            pct_change = round(((close_price - prev_close) / prev_close) * 100, 2)
            
            print(f"Closing price for {ticker_symbol}: {close_price}, Previous close: {prev_close}, Change: {pct_change}%")
            return close_price, pct_change
        
        # If not enough data, use intraday change
        if not current_data.empty:
            close_price = round(current_data["Close"].iloc[-1], 2)
            open_price = round(current_data["Open"].iloc[-1], 2)
            pct_change = round(((close_price - open_price) / open_price) * 100, 2)
            
            print(f"Closing price for {ticker_symbol}: {close_price}, Open: {open_price}, Intraday change: {pct_change}%")
            return close_price, pct_change
            
        print(f"Empty data for {ticker_symbol} in API response")
        return "N/A", 0.0
    except Exception as e:
        print(f"Error retrieving price for {ticker_symbol}: {e}")
        return "Error", 0.0

def get_daily_data(ticker_symbol):
    """Generic function to get daily chart data for any ticker"""
    try:
        # Add delay to avoid API limits
        time.sleep(0.5)
        
        stock = yf.Ticker(ticker_symbol)
        # Get data for the last day with 5-minute intervals
        data = stock.history(period="1d", interval="5m")
        
        if data is not None and not data.empty:
            print(f"Retrieved data for {ticker_symbol}: {len(data)} points")
        else:
            print(f"No data retrieved for {ticker_symbol} chart")
        
        return data
    except Exception as e:
        print(f"Error retrieving daily data for {ticker_symbol}: {e}")
        return None

class StockPriceDisplay:
    def __init__(self, root, ticker1="PG", ticker2="KO", show_chart=False):
        self.root = root
        self.ticker1 = ticker1
        self.ticker2 = ticker2
        self.root.overrideredirect(True)  # Remove borders and title bar
        self.root.attributes('-topmost', True)  # Keep window always on top
        self.root.attributes('-alpha', 0.85)  # Make window semi-transparent
        
        # Window configuration
        self.root.configure(bg='black')
        self.root.wm_attributes('-transparentcolor', 'black')  # Make black fully transparent
        self.root.geometry("+0+0")  # Initial position at top-left
        
        # Main frame
        self.main_frame = tk.Frame(root, bg="black")
        self.main_frame.pack(padx=2, pady=2)
        
        # Horizontal frame for labels and chart
        self.horizontal_frame = tk.Frame(self.main_frame, bg="black")
        self.horizontal_frame.pack(fill=tk.X)
        
        # Frame for price and change labels (on the left)
        self.price_frame = tk.Frame(self.horizontal_frame, bg="black")
        self.price_frame.pack(side=tk.LEFT)
        
        # Constant for Windows taskbar color
        self.TASKBAR_COLOR = "#F1F1F1"  # Light gray similar to Windows 10/11 taskbar

        # Custom font
        self.custom_font = font.Font(family="Arial", size=10, weight="bold")
        self.pct_font = font.Font(family="Arial", size=8)

        # Frame for first ticker (first row)
        self.ticker1_frame = tk.Frame(self.price_frame, bg=self.TASKBAR_COLOR)
        self.ticker1_frame.pack(fill=tk.X, anchor=tk.W)
        
        # Label for ticker1 price (on the same line as percentage)
        self.ticker1_price_label = tk.Label(
            self.ticker1_frame, 
            text=f"{self.ticker1}: Loading...", 
            fg="#333333",
            bg=self.TASKBAR_COLOR,
            font=self.custom_font,
            padx=5,
            pady=2
        )
        self.ticker1_price_label.pack(side=tk.LEFT)
        
        # Label for ticker1 percentage change (on the same line as price)
        self.ticker1_pct_label = tk.Label(
            self.ticker1_frame, 
            text="0.00%", 
            fg="#333333",
            bg=self.TASKBAR_COLOR,
            font=self.pct_font,
            padx=5,
            pady=2
        )
        self.ticker1_pct_label.pack(side=tk.LEFT)

        # Frame for second ticker (second row)
        self.ticker2_frame = tk.Frame(self.price_frame, bg=self.TASKBAR_COLOR)
        self.ticker2_frame.pack(fill=tk.X, anchor=tk.W)
        
        # Label for ticker2 price
        self.ticker2_price_label = tk.Label(
            self.ticker2_frame, 
            text=f"{self.ticker2}: Loading...", 
            fg="#333333",
            bg=self.TASKBAR_COLOR,
            font=self.custom_font,
            padx=5,
            pady=2
        )
        self.ticker2_price_label.pack(side=tk.LEFT)
        
        # Label for ticker2 percentage change
        self.ticker2_pct_label = tk.Label(
            self.ticker2_frame, 
            text="0.00%", 
            fg="#333333",
            bg=self.TASKBAR_COLOR,
            font=self.pct_font,
            padx=5,
            pady=2
        )
        self.ticker2_pct_label.pack(side=tk.LEFT)
        
        if show_chart:
            # Frame for chart (now on the right)
            self.chart_frame = tk.Frame(self.horizontal_frame, bg="black")
            self.chart_frame.pack(side=tk.RIGHT, pady=5)
            
            # Initialize chart
            self.fig, self.ax = plt.subplots(figsize=(1.75, 0.75), facecolor=self.TASKBAR_COLOR)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.config(highlightthickness=0)  # Remove canvas border
            self.canvas_widget.pack()
            
            # Configure chart appearance
            self.ax.set_facecolor(self.TASKBAR_COLOR)  # Taskbar color
            self.ax.tick_params(axis='x', colors='black', labelsize=6)
            self.ax.tick_params(axis='y', colors='black', labelsize=6)
            for spine in self.ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.5)
        
        # Add drag functionality
        self.main_frame.bind("<ButtonPress-1>", self.start_move)
        self.main_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.main_frame.bind("<B1-Motion>", self.on_motion)
        self.price_frame.bind("<ButtonPress-1>", self.start_move)
        self.price_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.price_frame.bind("<B1-Motion>", self.on_motion)
        
        # Bind ticker1 frame
        self.ticker1_frame.bind("<ButtonPress-1>", self.start_move)
        self.ticker1_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.ticker1_frame.bind("<B1-Motion>", self.on_motion)
        self.ticker1_price_label.bind("<ButtonPress-1>", self.start_move)
        self.ticker1_price_label.bind("<ButtonRelease-1>", self.stop_move)
        self.ticker1_price_label.bind("<B1-Motion>", self.on_motion)
        self.ticker1_pct_label.bind("<ButtonPress-1>", self.start_move)
        self.ticker1_pct_label.bind("<ButtonRelease-1>", self.stop_move)
        self.ticker1_pct_label.bind("<B1-Motion>", self.on_motion)
        
        # Bind ticker2 frame
        self.ticker2_frame.bind("<ButtonPress-1>", self.start_move)
        self.ticker2_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.ticker2_frame.bind("<B1-Motion>", self.on_motion)
        self.ticker2_price_label.bind("<ButtonPress-1>", self.start_move)
        self.ticker2_price_label.bind("<ButtonRelease-1>", self.stop_move)
        self.ticker2_price_label.bind("<B1-Motion>", self.on_motion)
        self.ticker2_pct_label.bind("<ButtonPress-1>", self.start_move)
        self.ticker2_pct_label.bind("<ButtonRelease-1>", self.stop_move)
        self.ticker2_pct_label.bind("<B1-Motion>", self.on_motion)
        
        if show_chart:
            self.canvas_widget.bind("<ButtonPress-1>", self.start_move)
            self.canvas_widget.bind("<ButtonRelease-1>", self.stop_move)
            self.canvas_widget.bind("<B1-Motion>", self.on_motion)
        
        # Right-click context menu
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Esci", command=self.exit_app)
        self.main_frame.bind("<Button-3>", self.show_menu)
        self.price_frame.bind("<Button-3>", self.show_menu)
        self.ticker1_frame.bind("<Button-3>", self.show_menu)
        self.ticker2_frame.bind("<Button-3>", self.show_menu)
        self.ticker1_price_label.bind("<Button-3>", self.show_menu)
        self.ticker1_pct_label.bind("<Button-3>", self.show_menu)
        self.ticker2_price_label.bind("<Button-3>", self.show_menu)
        self.ticker2_pct_label.bind("<Button-3>", self.show_menu)
        
        if show_chart:
            self.canvas_widget.bind("<Button-3>", self.show_menu)
        
        # Start thread to update prices and chart
        self.update_thread = threading.Thread(target=self.update_price, daemon=True)
        self.update_thread.start()
        
        # Position near taskbar
        self.position_near_taskbar()
        
        # Ensure window stays always on top
        self.ensure_topmost()
    
    def position_near_taskbar(self):
        # Position window in bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position to be near taskbar
        window_width = 196
        window_height = 60
        x_position = screen_width - window_width - 10
        y_position = screen_height - window_height - 10
        
        self.root.geometry(f"+{x_position}+{y_position}")
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        self.x = None
        self.y = None
    
    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)
    
    def exit_app(self):
        self.root.quit()
    
    def update_chart(self, data):
        if data is None or data.empty:
            print("No data available to update chart")
            return
        
        # Verify chart is initialized
        if not hasattr(self, 'ax') or data is None or data.empty:
            return
        
        self.ax.clear()
        
        # Configure chart appearance
        self.ax.set_facecolor(self.TASKBAR_COLOR)
        
        # Hide ticks and labels on axes
        self.ax.tick_params(axis='x', colors='#333333', labelsize=6, labelbottom=False, bottom=False)
        self.ax.tick_params(axis='y', colors='#333333', labelsize=6, labelleft=False, left=False)
        
        # Hide chart borders
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
        # Plot closing prices
        last_price = data["Close"].iloc[-1]
        first_price = data["Close"].iloc[0]
        color = 'green' if last_price >= first_price else 'red'
        
        # Draw line
        self.ax.plot(data.index, data["Close"], color=color, linewidth=1.5)
        
        # Add points for each data point (reduced to avoid overloading chart)
        step = max(1, len(data) // 10)  # Show about 10 points on chart
        self.ax.plot(data.index[::step], data["Close"].iloc[::step], 'o', color=color, markersize=2)
        
        # Remove title and axis labels
        self.ax.set_title('')
        self.ax.set_xlabel('')
        self.ax.set_ylabel('')
        
        # Remove grid
        self.ax.grid(False)
        
        # Update canvas
        self.fig.tight_layout(pad=0.0)
        self.canvas.draw_idle()
    
    def update_price(self):
        while True:
            try:
                # Update ticker1 price and change
                ticker1_price, ticker1_pct_change = get_stock_price(self.ticker1)
                self.ticker1_price_label.config(text=f"{self.ticker1}: {ticker1_price}")
                
                # Set color based on change for ticker1
                ticker1_color = "darkgreen" if ticker1_pct_change >= 0 else "darkred"
                ticker1_sign = "+" if ticker1_pct_change > 0 else ""
                self.ticker1_pct_label.config(text=f"{ticker1_sign}{ticker1_pct_change}%", fg=ticker1_color)
                
                # Update ticker2 price and change
                ticker2_price, ticker2_pct_change = get_stock_price(self.ticker2)
                self.ticker2_price_label.config(text=f"{self.ticker2}: {ticker2_price}")
                
                # Set color based on change for ticker2
                ticker2_color = "darkgreen" if ticker2_pct_change >= 0 else "darkred"
                ticker2_sign = "+" if ticker2_pct_change > 0 else ""
                self.ticker2_pct_label.config(text=f"{ticker2_sign}{ticker2_pct_change}%", fg=ticker2_color)
                
                print(f"UI Update: {self.ticker1}={ticker1_price} ({ticker1_pct_change}%), {self.ticker2}={ticker2_price} ({ticker2_pct_change}%)")
                
                # Update chart every minute (using ticker1 for the chart)
                data = get_daily_data(self.ticker1)
                self.update_chart(data)
            except Exception as e:
                print(f"Error updating UI: {e}")
            
            # Reduce update interval to 5 minutes to decrease API calls
            time.sleep(60 * 5)
    
    def ensure_topmost(self):
        """Ensure window always stays on top."""
        self.root.attributes('-topmost', True)
        # Call this function every 10 seconds
        self.root.after(10 * 1000, self.ensure_topmost)

def main():
    parser = argparse.ArgumentParser(description="Stock Price Display Widget")
    parser.add_argument('tickers', type=str, nargs='*', default=["PG", "KO"], 
                        help="Ticker symbols to display (provide 0-2 symbols, defaults: PG, KO)")
    parser.add_argument('--show-chart', action='store_true', help="Show price chart")
    args = parser.parse_args()
    
    # Use the first two tickers provided, or fall back to defaults if not enough are provided
    ticker1 = args.tickers[0] if len(args.tickers) > 0 else "PG"
    ticker2 = args.tickers[1] if len(args.tickers) > 1 else "KO"
    
    root = tk.Tk()
    app = StockPriceDisplay(root, ticker1=ticker1, ticker2=ticker2, show_chart=args.show_chart)
    root.mainloop()
    
if __name__ == "__main__":
    main()
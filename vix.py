import matplotlib.pyplot as plt
import numpy as np

def payoff_long_call(strike_price, premium, stock_price, multiplier=100):
    return np.where(stock_price > strike_price, multiplier * (stock_price - strike_price - premium), -multiplier * premium)

def payoff_short_call(strike_price, premium, stock_price, multiplier=100):
    return np.where(stock_price > strike_price, multiplier * (premium - (stock_price - strike_price)), multiplier * premium)

def plot_vix_payoff_chart():
    vix_long_call_strike_price = 30
    vix_long_call_premium = 0.6
    vix_short_call_strike_price = 70
    vix_short_call_premium = 0.1
    vix_multiplier = 1
    stock_prices = np.linspace(10, 100, 100)
    
    vix_long_call_payoffs = payoff_long_call(vix_long_call_strike_price, vix_long_call_premium, stock_prices, vix_multiplier * 100)
    vix_short_call_payoffs = payoff_short_call(vix_short_call_strike_price, vix_short_call_premium, stock_prices, vix_multiplier * 100)
    
    combined_payoffs = vix_long_call_payoffs + vix_short_call_payoffs

    plt.figure(figsize=(10, 6))
    plt.plot(stock_prices, combined_payoffs, label='Combined Payoff', color='green')
    plt.axhline(0, color='black', lw=2)
    
    max_loss = np.min(combined_payoffs)
    max_loss_stock_price = stock_prices[np.argmin(combined_payoffs)]
    plt.annotate(f'Max Loss: {max_loss:.2f}\nStock Price: {max_loss_stock_price:.2f}', 
                 xy=(max_loss_stock_price, max_loss), xytext=(max_loss_stock_price, max_loss - 1000),
                 arrowprops=dict(facecolor='red', shrink=0.05), fontsize=12, color='red')

    breakeven_price = None
    for index in range(0, len(combined_payoffs) - 1):
        if combined_payoffs[index] > 0:
            breakeven_price = stock_prices[index]
            break
    
    plt.annotate(f'Breakeven: {breakeven_price:.2f}', 
                 xy=(breakeven_price, 0), xytext=(breakeven_price, 1000),
                 arrowprops=dict(facecolor='blue', shrink=0.05), fontsize=12, color='blue')
    
    plt.title('Payoff Chart for Combined Long Call and Short Call on VIX')
    plt.xlabel('VIX Price at Expiration')
    plt.ylabel('Profit / Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    plot_vix_payoff_chart()
import matplotlib.pyplot as plt
import numpy as np

def payoff_short_put(strike_price, premium, stock_price, multiplier=5):
    return np.where(stock_price < strike_price, multiplier * (premium - (strike_price - stock_price)), multiplier * premium)

def payoff_long_call(strike_price, premium, stock_price, multiplier=100):
    return np.where(stock_price > strike_price, multiplier * (stock_price - strike_price - premium), -multiplier * premium)

def plot_combined_payoff_chart():
    mes_strike_price = 5800
    mes_premium = 20
    vix_strike_price = 30
    vix_premium = 0.5
    vix_multiplier = 2
    initial_vix_price = 20
    stock_prices = np.linspace(4500, 6000, 100)
    
    mes_payoffs = payoff_short_put(mes_strike_price, mes_premium, stock_prices)
    vix_prices = initial_vix_price + (5800 - stock_prices) * (20 / 580)  # Assuming VIX increases 20 points for each 10% MES decrease
    vix_payoffs = payoff_long_call(vix_strike_price, vix_premium, vix_prices, vix_multiplier * 100)
    
    combined_payoffs = mes_payoffs + vix_payoffs

    plt.figure(figsize=(10, 6))
    plt.plot(stock_prices, mes_payoffs, label='Short Put on MES')
    plt.plot(stock_prices, vix_payoffs, label='Long Calls on VIX')
    plt.plot(stock_prices, combined_payoffs, label='Combined Payoff')
    plt.axhline(0, color='black', lw=2)
    plt.axvline(mes_strike_price, color='red', linestyle='--', lw=2)
    
    max_loss = np.min(combined_payoffs)
    max_loss_stock_price = stock_prices[np.argmin(combined_payoffs)]
    plt.annotate(f'Max Loss: {max_loss:.2f}\nStock Price: {max_loss_stock_price:.2f}', 
                 xy=(max_loss_stock_price, max_loss), xytext=(max_loss_stock_price, max_loss - 1000),
                 arrowprops=dict(facecolor='red', shrink=0.05), fontsize=12, color='red')
    
    breakeven_index = np.nonzero(np.isclose(combined_payoffs[::-1], 0.0))[0]
    
    # Print each stock price value for breakeven indices
    for index in breakeven_index:
        print(f'Breakeven index: {index}, Stock Price: {stock_prices[index]:.2f}, Combined Payoff: {combined_payoffs[index]:.2f}')

    if breakeven_index.size > 0:
        breakeven_price = stock_prices[breakeven_index.size]
        plt.annotate(f'Breakeven: {breakeven_price:.2f}', 
                     xy=(breakeven_price, 0), xytext=(breakeven_price, 1000),
                     arrowprops=dict(facecolor='blue', shrink=0.05), fontsize=12, color='blue')
    
    plt.title('Payoff Chart for Short Put on MES and Long Calls on VIX')
    plt.xlabel('MES Stock Price at Expiration')
    plt.ylabel('Profit / Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    plot_combined_payoff_chart()

import matplotlib.pyplot as plt
import numpy as np

def payoff_short_put(strike_price, premium, stock_price, multiplier=5):
    return np.where(stock_price < strike_price, multiplier * (premium - (strike_price - stock_price)), multiplier * premium)

def payoff_long_call(strike_price, premium, stock_price, multiplier=100):
    return np.where(stock_price > strike_price, multiplier * (stock_price - strike_price - premium), -multiplier * premium)

def plot_combined_payoff_chart():
    mes_strike_price = 5800
    mes_premium = 20
    vix_long_call_strike_price = 28
    vix_long_call_premium = 0.6
    vix_multiplier = 2
    initial_vix_price = 20
    initial_capital = 3000  # Define your initial capital here
    stock_prices = np.linspace(mes_strike_price * 0.8, mes_strike_price * 1.05, 100)
    
    mes_payoffs = payoff_short_put(mes_strike_price, mes_premium, stock_prices)
    vix_prices = initial_vix_price + (mes_strike_price - stock_prices) * (200 / mes_strike_price)  # Assuming VIX increases 20 points for each 10% MES decrease
    vix_long_call_payoffs = payoff_long_call(vix_long_call_strike_price, vix_long_call_premium, vix_prices, vix_multiplier * 100)
    
    combined_payoffs = mes_payoffs + vix_long_call_payoffs

    plt.figure(figsize=(10, 6))
    plt.plot(stock_prices, mes_payoffs, label='Short Put on MES @ ' + str(mes_strike_price))
    plt.plot(stock_prices, vix_long_call_payoffs, label='Long Calls on VIX @ ' + str(vix_long_call_strike_price))
    plt.plot(stock_prices, combined_payoffs, label='Combined Payoff', color='green')
    plt.axhline(0, color='black', lw=2)
    
    max_loss = np.min(combined_payoffs)
    max_loss_stock_price = stock_prices[np.argmin(combined_payoffs)]
    initial_credit = mes_premium * 5
    initial_debit = vix_long_call_premium * vix_multiplier * 100
    net_initial_credit = initial_credit - initial_debit
    max_loss_percent = (max_loss / (initial_capital - net_initial_credit)) * 100
    mes_percent_fall = -((mes_strike_price - max_loss_stock_price) / mes_strike_price) * 100
    plt.annotate(f'Max Loss: {max_loss:.2f} ({max_loss_percent:.2f}%)\nMES Price: {max_loss_stock_price:.2f} ({mes_percent_fall:.2f}%)', 
                 xy=(max_loss_stock_price, max_loss), xytext=(max_loss_stock_price, max_loss - 1000),
                 arrowprops=dict(facecolor='red', shrink=0.05), fontsize=12, color='red')

    breakeven_price = None
    for index in range(0, len(combined_payoffs) - 1):
        minimum_payoff = 9999
        if combined_payoffs[index] < minimum_payoff and combined_payoffs[index] > 0:
            breakeven_price = stock_prices[index]
    
    plt.annotate(f'Breakeven: {breakeven_price:.2f}', 
                 xy=(breakeven_price, 0), xytext=(breakeven_price, 1000),
                 arrowprops=dict(facecolor='blue', shrink=0.05), fontsize=12, color='blue')
    
    plt.title('Cassandra\'s Strategy - Initial Capital: ' + str(initial_capital))
    plt.xlabel('MES Stock Price at Expiration')
    plt.ylabel('Profit / Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    plot_combined_payoff_chart()
import matplotlib.pyplot as plt
import numpy as np

def payoff_short_put(strike_price, premium, stock_price, multiplier=5):
    return np.where(stock_price < strike_price, multiplier * (premium - (strike_price - stock_price)), multiplier * premium)

def payoff_long_call(strike_price, premium, stock_price, multiplier=100):
    return np.where(stock_price > strike_price, multiplier * (stock_price - strike_price - premium), -multiplier * premium)

def payoff_short_call(strike_price, premium, stock_price, multiplier=100):
    return np.where(stock_price > strike_price, multiplier * (premium - (stock_price - strike_price)), multiplier * premium)

def plot_combined_payoff_chart():
    mes_strike_price = 5800
    mes_premium = 20
    vix_long_call_strike_price = 30
    vix_long_call_premium = 0.6
    vix_short_call_strike_price = 70
    vix_short_call_premium = 0.1
    vix_multiplier = 2
    initial_vix_price = 20
    initial_capital = 5000
    stock_prices = np.linspace(mes_strike_price * 0.7, mes_strike_price * 1.1, 100)
    
    mes_payoffs = payoff_short_put(mes_strike_price, mes_premium, stock_prices)
    vix_prices = initial_vix_price + (mes_strike_price - stock_prices) * (200 / mes_strike_price)  # Assuming VIX increases 20 points for each 10% MES decrease
    vix_long_call_payoffs = payoff_long_call(vix_long_call_strike_price, vix_long_call_premium, vix_prices, vix_multiplier * 100)
    vix_short_call_payoffs = payoff_short_call(vix_short_call_strike_price, vix_short_call_premium, vix_prices, vix_multiplier * 100)
    
    combined_vix_payoffs = vix_long_call_payoffs + vix_short_call_payoffs
    combined_payoffs = mes_payoffs + combined_vix_payoffs

    plt.figure(figsize=(10, 6))
    plt.plot(stock_prices, mes_payoffs, label='Short Put on MES @ ' + str(mes_strike_price))
    plt.plot(stock_prices, combined_vix_payoffs, label=str(vix_multiplier) + ' x Bear Call VIX @ ' + str(vix_long_call_strike_price) + "/" + str(vix_short_call_strike_price), color='orange')
    plt.plot(stock_prices, combined_payoffs, label='Combined', color='green')
    plt.axhline(0, color='black', lw=2)
    plt.axvline(mes_strike_price, color='red', linestyle='--', lw=1)
    
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
    last_call_price = None
    minimum_payoff = 9999
    for index in range(0, len(combined_payoffs) - 1):
        if combined_payoffs[index] < minimum_payoff and combined_payoffs[index] > 0:
            breakeven_price = stock_prices[index]

    for index in range(0, len(combined_payoffs) - 1):
        if stock_prices[index] < breakeven_price  and combined_payoffs[index] < 0:
            last_call_price = stock_prices[index]
    

    mes_percent_breakeaven = -((mes_strike_price - breakeven_price) / mes_strike_price) * 100
    plt.annotate(f'Breakeven: {breakeven_price:.2f} ({mes_percent_breakeaven:.2f}%)', 
                 xy=(breakeven_price, 0), xytext=(breakeven_price, 1000),
                 arrowprops=dict(facecolor='blue', shrink=0.05), fontsize=12, color='blue')
    
    mes_percent_last_call = -((mes_strike_price - last_call_price) / mes_strike_price) * 100
    if last_call_price is not None:
        plt.annotate(f'Last call: {last_call_price:.2f} ({mes_percent_last_call:.2f}%)', 
                    xy=(last_call_price, 0), xytext=(last_call_price, -1400),
                    arrowprops=dict(facecolor='blue', shrink=0.05), 
                    fontsize=12, color='blue')
    
    plt.title('Cassandra\'s Strategy - Initial Capital: ' + str(initial_capital))
    plt.xlabel('MES Stock Price at Expiration')
    plt.ylabel('Profit / Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    plot_combined_payoff_chart()
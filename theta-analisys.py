import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

# Black-Scholes formula for put option price
def black_scholes_put(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

# Function to calculate strike price for a given delta
def strike_from_delta(S, T, r, sigma, delta):
    d1 = norm.ppf(delta) + sigma * np.sqrt(T)
    K = S * np.exp(-d1 * sigma * np.sqrt(T) + (r + 0.5 * sigma ** 2) * T)
    return K

# Parameters
S = 6000  # Current price of SP500
r = 0.01  # Risk-free interest rate
sigma = 0.2  # Volatility
days = 7  # Number of days to maturity

# Time to maturity (in years) for the specified number of days, ending 1 hour before expiration
T = np.linspace(days/252, 1/24/252, days + 1)
days_to_maturity = np.linspace(days, 1/24, days + 1)  # Days to maturity

# Calculate put prices for different times to maturity
K = 5950  # Strike price for delta 50
put_prices = [black_scholes_put(S, K, t, r, sigma) for t in T]

# Calculate strike price for delta 25
K_delta_25 = [strike_from_delta(S, t, r, sigma, 1 - 0.25) for t in T]
put_prices_delta_25 = [black_scholes_put(S, K, t, r, sigma) for K, t in zip(K_delta_25, T)]

# Calculate strike price for delta 75
K_delta_75 = [strike_from_delta(S, t, r, sigma, 1 - 0.75) for t in T]
put_prices_delta_75 = [black_scholes_put(S, K, t, r, sigma) for K, t in zip(K_delta_75, T)]

# Plotting the results
plt.figure(figsize=(10, 6))
plt.plot(days_to_maturity, put_prices, label='Put Option Price (Delta 50)', color='blue')
plt.plot(days_to_maturity, put_prices_delta_25, label='Put Option Price (Delta 25)', color='green')
plt.plot(days_to_maturity, put_prices_delta_75, label='Put Option Price (Delta 75)', color='red')

plt.gca().invert_xaxis()  # Invert the x-axis
plt.gca().yaxis.tick_right()  # Move y-axis to the right
plt.xlabel('Days to Maturity')
plt.ylabel('Put Option Price')
plt.title('Time Decay of Put Options on SP500 (Last 7 Days)')
plt.legend()
plt.grid(True)
plt.show()

import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

# Black-Scholes formula for put option price
def black_scholes_put(S, K, T, r, sigma):
    if T <= 0:  # Gestione del caso di scadenza (T=0)
        return max(K - S, 0)  # Valore intrinseco a scadenza
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

# Function to calculate strike price for a given delta
def strike_from_delta(S, T, r, sigma, delta):
    if T <= 0:  # Gestione del caso di scadenza (T=0)
        return S  # A scadenza, lo strike per qualsiasi delta è il prezzo spot
    d1 = norm.ppf(delta) + sigma * np.sqrt(T)
    K = S * np.exp(-d1 * sigma * np.sqrt(T) + (r + 0.5 * sigma ** 2) * T)
    return K

# Calcolo del theta (derivata rispetto al tempo)
def black_scholes_theta_put(S, K, T, r, sigma):
    if T <= 0:  # Gestione del caso di scadenza (T=0)
        return 0  # Il theta a scadenza è 0
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    theta = -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(-d2)
    return theta / 365  # Theta giornaliero

# Parameters
S = 5600  # Current price of SP500
r = 0.01  # Risk-free interest rate
sigma = 0.22  # Volatility
days = 180  # Number of days to maturity

# Time to maturity (in years) for the specified number of days, includendo la scadenza (T=0)
# Creating a non-linear distribution to better visualize the time decay effect
# More points close to expiration where theta changes more rapidly
T_values = np.concatenate([
    np.linspace(days/252, 30/252, 30),  # First 30 days, fewer points
    np.linspace(30/252, 7/252, 20),     # From 30 to 7 days
    np.linspace(7/252, 0, 16)           # Last 7 days, more points, including expiration
])
days_to_maturity = np.concatenate([
    np.linspace(days, 30, 30),
    np.linspace(30, 7, 20),
    np.linspace(7, 0, 16)               # Include exact expiration (0 days)
])

# Calculate put prices for different times to maturity
# Invece di usare uno strike fisso, calcola anche lo strike per il delta 50
K_delta_50 = [strike_from_delta(S, t, r, sigma, 1 - 0.5) for t in T_values]
put_prices = [black_scholes_put(S, k, t, r, sigma) for k, t in zip(K_delta_50, T_values)]

# Calculate strike price for delta 25
K_delta_25 = [strike_from_delta(S, t, r, sigma, 1 - 0.25) for t in T_values]
put_prices_delta_25 = [black_scholes_put(S, k, t, r, sigma) for k, t in zip(K_delta_25, T_values)]

# Calculate strike price for delta 75
K_delta_75 = [strike_from_delta(S, t, r, sigma, 1 - 0.75) for t in T_values]
put_prices_delta_75 = [black_scholes_put(S, k, t, r, sigma) for k, t in zip(K_delta_75, T_values)]

# Plotting the results
plt.figure(figsize=(12, 8))
plt.plot(days_to_maturity, put_prices, label='Put Option Price (Delta 50)', color='blue')
plt.plot(days_to_maturity, put_prices_delta_25, label='Put Option Price (Delta 25)', color='green')
plt.plot(days_to_maturity, put_prices_delta_75, label='Put Option Price (Delta 75)', color='red')

# Aggiungere annotazioni per i prezzi ad alcuni punti chiave
plt.annotate(f"{put_prices[0]:.2f}", (days_to_maturity[0], put_prices[0]), textcoords="offset points", 
             xytext=(0,10), ha='center')
plt.annotate(f"{put_prices[-1]:.2f}", (days_to_maturity[-1], put_prices[-1]), textcoords="offset points", 
             xytext=(0,10), ha='center')

plt.gca().invert_xaxis()  # Invert the x-axis
plt.gca().yaxis.tick_right()  # Move y-axis to the right
plt.xlabel('Days to Maturity')
plt.ylabel('Put Option Price')
plt.title('Time Decay of Put Options on SP500 (180 Days to Expiry)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

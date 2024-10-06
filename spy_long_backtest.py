import json
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Load API keys from JSON file
with open("config.json", "r") as file:
    config = json.load(file)
    fred_api_key = config["fred_api_key"]

# Function to get data from FRED
def fetch_fred_data(series_id, api_key):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    data = response.json()["observations"]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df

# Fetch VIX and S&P 500 data from FRED
vix_data = fetch_fred_data("VIXCLS", fred_api_key)
sp500_data = fetch_fred_data("SP500", fred_api_key)

# Define the ranges for the VIX_THRESHOLD and LOOKBACK_DAYS to test
best_return = -float('inf')  # Initialize best cumulative return to a very low value
best_vix_threshold = None
best_lookback_days = None

for VIX_THRESHOLD in range(30, 51, 1):  # Step by 5
    for LOOKBACK_DAYS in range(5, 20, 1):  # Step by 20

        # Calculate the overall percentile of each day's VIX value over the dataset
        vix_data["Percentile"] = vix_data["value"].rank(pct=True) * 100

        # Calculate the rolling percentile of each day's VIX value over the current lookback period
        vix_data["Rolling Percentile"] = (
            vix_data["value"]
            .rolling(window=LOOKBACK_DAYS)
            .apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1] * 100)
        )
        vix_data["Rolling Percentile"].fillna(vix_data["Percentile"], inplace=True)

        # Align the two datasets on their dates
        aligned_data = pd.concat([sp500_data, vix_data["Rolling Percentile"]], axis=1).dropna()

        # Filter out data where VIX is below the VIX_THRESHOLD
        blue_dot_data = aligned_data[aligned_data["Rolling Percentile"] < VIX_THRESHOLD].copy()

        # Calculate daily returns and filter out extreme outliers
        blue_dot_data["Daily Returns"] = blue_dot_data["value"].pct_change()
        threshold = 3 * blue_dot_data["Daily Returns"].std()
        blue_dot_data = blue_dot_data[
            (blue_dot_data["Daily Returns"] < threshold)
            & (blue_dot_data["Daily Returns"] > -threshold)
        ]

        # Calculate cumulative returns for the Long strategy
        if not blue_dot_data.empty:
            cumulative_blue_dot_returns = (blue_dot_data["Daily Returns"] + 1).cumprod() - 1
            blue_dot_return = cumulative_blue_dot_returns.iloc[-1] * 100
            print(f"VIX_THRESHOLD: {VIX_THRESHOLD} - LOOKBACK_DAYS: {LOOKBACK_DAYS} - Cumulative Return: {blue_dot_return:.2f}%")
            print(f"BEST VIX_THRESHOLD: {best_vix_threshold} - LOOKBACK_DAYS: {best_lookback_days} - Cumulative Return: {best_return:.2f}%")

            # Check if this is the best return so far
            if blue_dot_return > best_return:
                best_return = blue_dot_return
                best_vix_threshold = VIX_THRESHOLD
                best_lookback_days = LOOKBACK_DAYS

# Print the best VIX_THRESHOLD, LOOKBACK_DAYS, and cumulative return found
print(f"Best VIX_THRESHOLD: {best_vix_threshold}")
print(f"Best LOOKBACK_DAYS: {best_lookback_days}")
print(f"Highest Cumulative Return: {best_return:.2f}%")

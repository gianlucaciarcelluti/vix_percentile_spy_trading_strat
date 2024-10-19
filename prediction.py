import pandas as pd

# Load VIX data
vix_data = pd.read_json('VIXCLS.json')

# Convert VIX values to numeric
vix_data['value'] = pd.to_numeric(vix_data['value'], errors='coerce')

# Calculate the change in VIX
last_vix = vix_data['value'].iloc[-1]
previous_vix = vix_data['value'].iloc[-2]
vix_change = last_vix - previous_vix

# Regression coefficients from our analysis
beta_0 = -0.0003
beta_1 = -0.0021

# Predict SP500 return
predicted_return = beta_0 + beta_1 * vix_change

# Decision rule
if predicted_return < 0:
    decision = "Risk Off"
else:
    decision = "Risk On"

print(f"VIX Change: {vix_change}")
print(f"Predicted SP500 Return: {predicted_return}")
print(f"Decision: {decision}")

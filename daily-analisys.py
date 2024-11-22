import pandas as pd

pd.options.display.float_format = '{:.1f}%'.format

import matplotlib.pyplot as plt

# Leggi i dati dal file CSV
data = pd.read_csv('sp500_data.csv')

# Calcola la variazione percentuale tra la chiusura di un giorno e la chiusura del giorno successivo
data['Percent Change'] = data['close'].pct_change() * 100

# Rimuovi i valori NaN
data = data.dropna()

# Calcola il percentile del 15%
left_bound = data['Percent Change'].quantile(0.15)

# Crea un grafico ad istogrammi
plt.hist(data['Percent Change'], bins=500, edgecolor='blue')
plt.title('Distribuzione delle variazioni percentuali giornaliere con limite al 85%')
plt.xlabel('Variazione percentuale')
plt.ylabel('Frequenza')

# Aggiungi la linea verticale per il confine del 15%
plt.axvline(left_bound, color='red', linestyle='dashed', linewidth=1)

# Aggiungi il valore dell'ascissa in corrispondenza della linea verticale
plt.text(left_bound, plt.ylim()[1] * 0.85, f'{left_bound:.1f}%', color='red', ha='right')

# Calcola il numero di giorni medi in un anno
total_days = len(data)
years = (pd.to_datetime(data['date']).dt.year.max() - pd.to_datetime(data['date']).dt.year.min()) + 1
average_days_per_year = total_days / years

# Calcola il numero di giorni medi annui in cui il decremento è stato superiore al limite della linea verticale
days_above_left_bound = data[data['Percent Change'] < left_bound]
average_days_above_left_bound_per_year = len(days_above_left_bound) / years

# Aggiungi le informazioni finali nel grafico in alto a sinistra
plt.text(0.05, 0.95, f'Total yearly days: {average_days_per_year:.1f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
plt.text(0.05, 0.90, f'Yearly loss days: {average_days_above_left_bound_per_year:.1f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')

# Mostra il grafico
plt.show()

print(f'Numero di giorni medi in un anno: {average_days_per_year:.1f}')
print(f'Numero di giorni medi annui in cui il decremento è stato superiore al limite della linea verticale: {average_days_above_left_bound_per_year:.1f}')
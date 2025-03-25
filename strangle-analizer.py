import pandas as pd
import matplotlib.pyplot as plt

# Carica i dati dal file CSV
data = pd.read_csv('sp500_data.csv')
# Carica i dati del VIX dal file CSV
vix_data = pd.read_csv('vix_data.csv')

# Descrizione statistica dei dati VIX
print(vix_data.describe())

# Descrizione statistica dei dati
print(data.describe())

# Converte la colonna 'date' in formato datetime
data['date'] = pd.to_datetime(data['date'])
vix_data['date'] = pd.to_datetime(vix_data['date'])

# Unisce i due dataframe sul campo 'date'
# Rinomina la colonna 'close' in 'vix' nel dataframe vix_data
vix_data.rename(columns={'close': 'vix'}, inplace=True)
merged_data = pd.merge(data, vix_data[['date', 'vix']], on='date', how='left')

# Aggiungi la colonna 'vix' al dataframe originale
data['vix'] = merged_data['vix']

# Aggiungi una colonna 'year' al dataframe
data['year'] = pd.to_datetime(data['date']).dt.year

# Raggruppa i dati per anno e calcola la somma delle distanze dei prezzi di chiusura
annual_distance_sum = data.groupby('year')['close'].apply(lambda x: (x - x.shift()).abs().sum())

# Visualizza la somma delle distanze per anno
print(annual_distance_sum)

# Filtra i dati per includere solo le righe in cui il valore del VIX è minore di 24
filtered_data = data[data['vix'] < 24]

# Raggruppa i dati filtrati per anno e calcola la somma delle distanze dei prezzi di chiusura
annual_distance_sum_filtered = filtered_data.groupby('year')['close'].apply(lambda x: (x - x.shift()).abs().sum())

# Visualizza la somma delle distanze per anno per i dati filtrati
print(annual_distance_sum_filtered)
# Crea una tabella riassuntiva
summary_table = pd.DataFrame()

# Calcola il conteggio delle voci per ogni anno
summary_table['count'] = data.groupby('year')['close'].count()
# Calcola la somma delle differenze dei valori per ogni anno
summary_table['sum'] = data.groupby('year')['close'].apply(lambda x: (x - x.shift()).abs().sum())
# Calcola la media delle differenze dei valori per ogni anno
summary_table['avg'] = (summary_table['sum'] / summary_table['count']).apply(lambda x: int(x))

# Calcola il conteggio delle voci con VIX < 30
summary_table['count_30'] = data[data['vix'] < 30].groupby('year')['close'].count()
# Calcola la somma delle differenze dei valori con VIX < 30
summary_table['vix_30'] = data[data['vix'] < 30].groupby('year')['close'].apply(lambda x: (x - x.shift()).abs().sum())
# Calcola la media delle differenze dei valori per ogni anno
summary_table['avg_30'] = (summary_table['vix_30'] / summary_table['count_30']).apply(lambda x: int(x))

# Calcola il conteggio delle voci con VIX < 25
summary_table['count_25'] = data[data['vix'] < 25].groupby('year')['close'].count()
# Calcola la somma delle differenze dei valori con VIX < 25
summary_table['vix_25'] = data[data['vix'] < 25].groupby('year')['close'].apply(lambda x: (x - x.shift()).abs().sum())
# Calcola la media delle differenze dei valori per ogni anno
summary_table['avg_25'] = (summary_table['vix_25'] / summary_table['count_25']).apply(lambda x: int(x))

# Calcola il conteggio delle voci con VIX < 22
summary_table['count_22'] = data[data['vix'] < 22].groupby('year')['close'].count()
# Calcola la somma delle differenze dei valori con VIX < 22
summary_table['vix_22'] = data[data['vix'] < 22].groupby('year')['close'].apply(lambda x: (x - x.shift()).abs().sum())
# Calcola la media delle differenze dei valori per ogni anno
summary_table['avg_22'] = (summary_table['vix_22'] / summary_table['count_22']).apply(lambda x: int(x))

# Calcola il conteggio delle voci con VIX < 20
summary_table['count_20'] = data[data['vix'] < 20].groupby('year')['close'].count()
# Calcola la somma delle differenze dei valori con VIX < 20
summary_table['vix_20'] = data[data['vix'] < 20].groupby('year')['close'].apply(lambda x: (x - x.shift()).abs().sum())

# Visualizza la tabella riassuntiva
print(summary_table)

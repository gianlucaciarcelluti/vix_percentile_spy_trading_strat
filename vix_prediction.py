import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
import json

# Carica i dati storici di SP500 e VIX
def load_data():
    with open('VIXCLS.json', 'r') as f:
        vix_data = json.load(f)
    
    vix_df = pd.DataFrame(vix_data)
    vix_df['date'] = pd.to_datetime(vix_df['date'])
    vix_df['value'] = pd.to_numeric(vix_df['value'], errors='coerce')  # Converti i valori in numerici, sostituendo i non numerici con NaN
    vix_df.dropna(inplace=True)  # Rimuovi le righe con valori NaN
    vix_df.set_index('date', inplace=True)
    
    with open('SP500.json', 'r') as f:
        sp500_data = json.load(f)
    
    sp500_df = pd.DataFrame(sp500_data)
    sp500_df['date'] = pd.to_datetime(sp500_df['date'])
    sp500_df['value'] = pd.to_numeric(sp500_df['value'], errors='coerce')  # Converti i valori in numerici, sostituendo i non numerici con NaN
    sp500_df.dropna(inplace=True)  # Rimuovi le righe con valori NaN
    sp500_df.set_index('date', inplace=True)
    
    # Filtra le date comuni
    common_dates = sp500_df.index.intersection(vix_df.index)
    sp500_df = sp500_df.loc[common_dates]
    vix_df = vix_df.loc[common_dates]
    
    return sp500_df, vix_df

# Calcola le variazioni percentuali settimanali
def calculate_weekly_changes(df):
    return df['value'].pct_change(periods=5) * 100

# Trova la relazione tra le variazioni percentuali di SP500 e VIX utilizzando la regressione Ridge
def find_correlation(sp500_changes, vix_changes):
    sp500_changes = sp500_changes.dropna().values.reshape(-1, 1)
    vix_changes = vix_changes.dropna().values
    
    # Dividi il dataset in 80% per l'addestramento e 20% per il test
    X_train, X_test, y_train, y_test = train_test_split(sp500_changes, vix_changes, test_size=0.2, random_state=42)
    
    model = Ridge(alpha=1.0)  # Puoi regolare il parametro alpha per aumentare o diminuire la regolarizzazione
    model.fit(X_train, y_train)
    
    # Valuta il modello sui dati di test
    score = model.score(X_test, y_test)
    print(f"R^2 score del modello sui dati di test: {score:.2f}")
    
    return model

# Funzione per stimare la variazione del VIX in base alla variazione di SP500
def estimate_vix_change(sp500_change, model):
    return model.predict(np.array([[sp500_change]]))[0]

# Esempio di utilizzo
sp500_df, vix_df = load_data()
sp500_changes = calculate_weekly_changes(sp500_df).dropna()
vix_changes = calculate_weekly_changes(vix_df).dropna()

# Stampa le prime righe dei dati per verificare
print("Prime righe delle variazioni percentuali settimanali di SP500:")
print(sp500_changes.head())
print("Prime righe delle variazioni percentuali settimanali di VIX:")
print(vix_changes.head())

model = find_correlation(sp500_changes, vix_changes)

# Stima delle variazioni del VIX per una discesa di SP500 che va da -1 a -20
for sp500_change in range(-1, -21, -1):
    vix_estimated_change = estimate_vix_change(sp500_change, model) / 1.5
    print(f"Per una discesa del {sp500_change}% di SP500, si stima che il VIX salirà di {vix_estimated_change:.2f}%")
import pandas as pd
import re
from sqlalchemy import create_engine, text, MetaData, Table, Column, Float, Text, Date, TIMESTAMP, Integer
import csv
from io import StringIO

# CONFIGURA QUI LA TUA CONNESSIONE
DB_URI = "postgresql://postgres:H3mX5x1TxP09lbI@130.185.118.107:30007/ibkr"
CSV_PATH = "data/ibkr/U15963464_20250101_20250508.csv"

# Leggi tutto il CSV come testo
with open(CSV_PATH, encoding="utf-8") as f:
    lines = f.readlines()

# Trova tutte le intestazioni e le relative righe trade
trade_blocks = []
current_header = None
for line in lines:
    if line.startswith("Trades,Header,DataDiscriminator"):
        current_header = next(csv.reader([line]))
    elif line.startswith("Trades,Header"):
        current_header = next(csv.reader([line]))
    elif line.startswith("Trades,Data,Order"):
        fields = next(csv.reader([line]))
        # Allinea la lunghezza
        if len(fields) < len(current_header):
            fields += [""] * (len(current_header) - len(fields))
        trade_blocks.append(dict(zip(current_header, fields)))

df = pd.DataFrame(trade_blocks)

# Conversione colonne numeriche
numeric_cols = [
    "Quantity", "T. Price", "Proceeds", "Comm/Fee", "Basis", "Realized P/L", "MTM P/L"
]
for col in numeric_cols:
    if col in df.columns:
        if col == "Quantity":
            df[col] = df[col].str.replace(",", "").astype(float)
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    else:
        df[col] = None

df["Date/Time"] = pd.to_datetime(df["Date/Time"], errors="coerce")

# Cerca la colonna delle commissioni
df["Comm_Fee"] = pd.to_numeric(
    df.get("Comm/Fee", pd.NA).fillna(df.get("Comm in EUR", pd.NA)), errors="coerce"
)

# --- Arricchisci con info opzioni (strike, expiry, tipo, underlying) ---
# Carica la tabella "Financial Instrument Information" dal CSV
fininfo_lines = []
fininfo_header = None
for i, line in enumerate(lines):
    if line.startswith("Financial Instrument Information,Header,Asset Category"):
        fininfo_header = [h.strip() for h in line.strip().split(",")[2:]]
    elif line.startswith("Financial Instrument Information,Data"):
        fininfo_lines.append(line.strip().split(",", 2)[2])

fininfo = []
for line in fininfo_lines:
    fields = [f.strip() for f in line.split(",")]
    fields += [""] * (len(fininfo_header) - len(fields))
    fininfo.append(dict(zip(fininfo_header, fields)))
df_info = pd.DataFrame(fininfo)

# Crea dizionario symbol->info
info_map = {}
for _, row in df_info.iterrows():
    info_map[row.get("Symbol", "")] = row

# Funzione per estrarre info opzione
def enrich_option(row):
    symbol = row["Symbol"]
    info = info_map.get(symbol, {})
    row["option_strike"] = info.get("Strike")
    row["option_expiry"] = info.get("Expiry")
    row["option_type"] = info.get("Type")
    row["option_underlying"] = info.get("Underlying")
    row["option_multiplier"] = info.get("Multiplier")
    return row

df = df.apply(enrich_option, axis=1)

print(df.columns)
print(df.head())

# --- CREA TABELLA E INSERISCI DATI ---
engine = create_engine(DB_URI)

metadata = MetaData()
ibkr_trades = Table(
    "ibkr_trades", metadata,
    Column("id", Integer, primary_key=True),
    Column("asset_category", Text),
    Column("currency", Text),
    Column("symbol", Text),
    Column("datetime", TIMESTAMP),
    Column("quantity", Float),
    Column("t_price", Float),
    Column("c_price", Float),
    Column("proceeds", Float),
    Column("comm_fee", Float),
    Column("basis", Float),
    Column("realized_pl", Float),
    Column("mtm_pl", Float),
    Column("code", Text),
    Column("option_strike", Float),
    Column("option_expiry", Date),
    Column("option_type", Text),
    Column("option_underlying", Text),
    Column("option_multiplier", Float),
    # UNIQUE constraint is already in CREATE TABLE
)

create_table_sql = """
CREATE TABLE IF NOT EXISTS ibkr_trades (
    id SERIAL PRIMARY KEY,
    asset_category TEXT,
    currency TEXT,
    symbol TEXT,
    datetime TIMESTAMP,
    quantity FLOAT,
    t_price FLOAT,
    c_price FLOAT,
    proceeds FLOAT,
    comm_fee FLOAT,
    basis FLOAT,
    realized_pl FLOAT,
    mtm_pl FLOAT,
    code TEXT,
    option_strike FLOAT,
    option_expiry DATE,
    option_type TEXT,
    option_underlying TEXT,
    option_multiplier FLOAT,
    UNIQUE(asset_category, symbol, datetime, quantity, t_price)
);
"""

with engine.begin() as conn:
    conn.execute(text(create_table_sql))

# Prepara i dati da inserire
def parse_float(x):
    try:
        return float(x)
    except:
        return None

def parse_date(x):
    try:
        return pd.to_datetime(x).date()
    except:
        return None

records = []
for _, row in df.iterrows():
    records.append({
        "asset_category": row.get("Asset Category"),
        "currency": row.get("Currency"),
        "symbol": row.get("Symbol"),
        "datetime": row.get("Date/Time"),
        "quantity": row.get("Quantity"),
        "t_price": row.get("T. Price"),
        "c_price": parse_float(row.get("C. Price")),
        "proceeds": row.get("Proceeds"),
        "comm_fee": row.get("Comm_Fee"),
        "basis": row.get("Basis"),
        "realized_pl": row.get("Realized P/L"),
        "mtm_pl": row.get("MTM P/L"),
        "code": row.get("Code"),
        "option_strike": parse_float(row.get("option_strike")),
        "option_expiry": parse_date(row.get("option_expiry")),
        "option_type": row.get("option_type"),
        "option_underlying": row.get("option_underlying"),
        "option_multiplier": parse_float(row.get("option_multiplier")),
    })

# Inserisci i dati evitando duplicati
from sqlalchemy.dialects.postgresql import insert

with engine.begin() as conn:
    for rec in records:
        stmt = insert(ibkr_trades).values(**rec)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["asset_category", "symbol", "datetime", "quantity", "t_price"]
        )
        conn.execute(stmt)

print("Importazione completata.")
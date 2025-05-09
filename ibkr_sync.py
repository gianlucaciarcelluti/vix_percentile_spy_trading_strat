from ib_insync import IB
import psycopg2
import pandas as pd
from datetime import datetime

# Configurazioni
IB_HOST = '127.0.0.1'
IB_PORT = 4002   # Usa 4001 se IB Gateway
DB_CONN = "dbname=ibkr user=postgres password=H3mX5x1TxP09lbI host=130.185.118.107 port=30007"

def connect_ib():
    ib = IB()
    ib.connect(IB_HOST, IB_PORT, clientId=0)
    return ib

def fetch_executions(ib):
    executions = ib.reqExecutions()
    rows = []
    for trade in executions:
        e = trade.execution
        c = trade.contract
        rows.append({
            "exec_id": e.execId,
            "symbol": c.symbol,
            "action": e.side,
            "quantity": e.shares,
            "price": e.price,
            "currency": c.currency,
            "time": e.time,
            "exchange": c.exchange,
            "side": e.side,
            "account": e.acctNumber,
            "order_id": e.orderId,
            "contract_type": c.secType,
            "strike": c.strike if c.secType == 'OPT' else None,
            "expiry": datetime.strptime(c.lastTradeDateOrContractMonth, "%Y%m%d").date() if (c.secType == 'OPT' and c.lastTradeDateOrContractMonth) else None,
            "option_right": c.right if c.secType == 'OPT' else None,
            "multiplier": c.multiplier if c.secType == 'OPT' else None
        })
    return pd.DataFrame(rows)

def save_to_postgres(df):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO executions (
                exec_id, symbol, action, quantity, price, currency, time, exchange, side,
                account, order_id, contract_type, strike, expiry, option_right, multiplier
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (exec_id) DO NOTHING
        """, (
            row.exec_id, row.symbol, row.action, row.quantity, row.price, row.currency,
            row.time, row.exchange, row.side, row.account, row.order_id,
            row.contract_type, row.strike, row.expiry, row.option_right, row.multiplier
        ))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ib = connect_ib()
    df = fetch_executions(ib)
    print(f"✅ Recuperate {len(df)} esecuzioni.")
    save_to_postgres(df)
    print("📥 Dati salvati nel database.")
    ib.disconnect()

import sqlite3
import pandas as pd

CSV_PATH = "data/raw/synthetic_checkouts.csv"

DB_PATH = "data/revenue_recovery.db"

df = pd.read_csv(CSV_PATH)

conn = sqlite3.connect(DB_PATH)

df.to_sql(
    "checkouts",
    conn,
    if_exists="append",
    index=False
)

print(f"Inserted {len(df)} rows")

conn.close()
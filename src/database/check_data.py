import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/revenue_recovery.db"
)

query = """
SELECT *
FROM checkouts
LIMIT 5
"""

df = pd.read_sql(query, conn)

print(df)

conn.close()
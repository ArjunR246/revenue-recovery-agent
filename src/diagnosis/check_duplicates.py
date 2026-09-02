import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "data/revenue_recovery.db"
)

df = pd.read_sql(
    "SELECT * FROM checkouts",
    conn
)

conn.close()

print("\nTotal Rows")
print(len(df))

# ----------------------------------
# REMOVE UNIQUE IDS
# ----------------------------------

duplicate_check_df = df.drop(
    columns=[
        "checkout_id",
        "timestamp"
    ]
)

duplicate_count = duplicate_check_df.duplicated().sum()

print("\nExact Duplicate Rows")
print(duplicate_count)

duplicate_percent = (
    duplicate_count / len(df)
) * 100

print("\nDuplicate Percentage")
print(f"{duplicate_percent:.2f}%")
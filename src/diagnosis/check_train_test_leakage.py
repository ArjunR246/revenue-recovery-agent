import sqlite3

import pandas as pd

from sklearn.model_selection import train_test_split

# ==========================================
# LOAD DATA
# ==========================================

conn = sqlite3.connect(
    "data/revenue_recovery.db"
)

df = pd.read_sql(
    "SELECT * FROM checkouts",
    conn
)

conn.close()

# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

train_df, test_df = train_test_split(
    df,
    test_size=0.20,
    random_state=42,
    stratify=df["dropoff_cause"]
)

# ==========================================
# REMOVE COLUMNS THAT SHOULD NOT BE USED
# FOR LEAKAGE CHECKING
# ==========================================

train_sig = train_df.drop(
    columns=[
        "checkout_id",
        "timestamp",
        "dropoff_cause"
    ]
)

test_sig = test_df.drop(
    columns=[
        "checkout_id",
        "timestamp",
        "dropoff_cause"
    ]
)

# ==========================================
# CONVERT EACH ROW INTO A STRING SIGNATURE
# ==========================================

train_rows = set(
    train_sig
    .fillna("NULL")
    .astype(str)
    .apply(
        lambda row: "|".join(row),
        axis=1
    )
)

test_rows = set(
    test_sig
    .fillna("NULL")
    .astype(str)
    .apply(
        lambda row: "|".join(row),
        axis=1
    )
)

# ==========================================
# FIND OVERLAP
# ==========================================

overlap = train_rows.intersection(
    test_rows
)

# ==========================================
# REPORT
# ==========================================

print("\n========================================")
print("TRAIN / TEST LEAKAGE CHECK")
print("========================================")

print("\nTraining Rows")
print(len(train_rows))

print("\nTesting Rows")
print(len(test_rows))

print("\nRows Appearing In Both Train And Test")
print(len(overlap))

leakage_percentage = (
    len(overlap) / len(test_rows)
) * 100

print("\nLeakage Percentage")
print(f"{leakage_percentage:.4f}%")
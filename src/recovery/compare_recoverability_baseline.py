import sqlite3
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import brier_score_loss


# ==========================================
# LOAD DATA
# ==========================================

conn = sqlite3.connect("data/revenue_recovery.db")

df = pd.read_sql(
    "SELECT * FROM checkouts",
    conn
)

conn.close()


# ==========================================
# SAME TRAIN / TEST SPLIT AS STAGE 4B
# ==========================================

train_df, test_df = train_test_split(
    df,
    test_size=0.20,
    random_state=42,
    stratify=df["was_recovered"]
)


# ==========================================
# NAIVE ROOT-CAUSE BASELINE
# ==========================================

# Calculate recovery rate for each root cause
# using ONLY the training data.

cause_rates = (
    train_df
    .groupby("dropoff_cause")["was_recovered"]
    .mean()
)

print("\nRoot Cause Baseline Rates")
print(cause_rates)


# Assign each test row the average recovery
# rate of its root cause.

baseline_predictions = (
    test_df["dropoff_cause"]
    .map(cause_rates)
)


# ==========================================
# BRIER SCORE
# ==========================================

baseline_brier = brier_score_loss(
    test_df["was_recovered"],
    baseline_predictions
)

print("\nNaive Baseline Brier Score")
print(round(baseline_brier, 4))

print("\nYour Stage 4b Model Brier Score")
print(0.2065)

print("\nImprovement")
print(
    round(
        baseline_brier - 0.2065,
        4
    )
)
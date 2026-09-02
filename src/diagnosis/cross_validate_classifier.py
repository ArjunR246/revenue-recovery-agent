import sqlite3
import pandas as pd

from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score

from xgboost import XGBClassifier

# ----------------------------------
# LOAD DATA
# ----------------------------------

conn = sqlite3.connect(
    "data/revenue_recovery.db"
)

df = pd.read_sql(
    "SELECT * FROM checkouts",
    conn
)

conn.close()

# ----------------------------------
# FEATURES
# ----------------------------------

feature_columns = [
    "amount",
    "payment_method",
    "device_type",
    "session_duration_seconds",
    "inactivity_seconds",
    "retry_count",
    "checkout_step_reached",
    "network_quality",
    "payment_status",
    "failure_reason_code",
    "otp_attempts",
    "upi_collect_expired"
]

X = df[feature_columns]

X = pd.get_dummies(X)

label_map = {
    "PRICE_HESITATION": 0,
    "PAYMENT_FAILURE": 1,
    "OTP_FRICTION": 2,
    "DISTRACTION_TIMEOUT": 3
}

y = df["dropoff_cause"].map(label_map)

# ----------------------------------
# MODEL
# ----------------------------------

model = XGBClassifier(
    objective="multi:softmax",
    num_class=4,
    random_state=42,
    n_estimators=100,
    max_depth=4
)

# ----------------------------------
# 5-FOLD CV
# ----------------------------------

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scores = cross_val_score(
    model,
    X,
    y,
    cv=cv,
    scoring="accuracy"
)

print("\nFold Accuracies")

for i, score in enumerate(scores, start=1):
    print(f"Fold {i}: {score:.4f}")

print("\nMean Accuracy")
print(scores.mean())

print("\nStd Deviation")
print(scores.std())
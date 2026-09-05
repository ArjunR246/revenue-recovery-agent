import sqlite3
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

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

print("Rows loaded:", len(df))

# ----------------------------------
# FEATURES AND TARGET
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

target_column = "dropoff_cause"

X = df[feature_columns]

y = df[target_column]

# ----------------------------------
# ONE-HOT ENCODING
# ----------------------------------

X = pd.get_dummies(X)

# ----------------------------------
# ENCODE TARGET LABELS
# ----------------------------------

label_map = {
    "PRICE_HESITATION": 0,
    "PAYMENT_FAILURE": 1,
    "OTP_FRICTION": 2,
    "DISTRACTION_TIMEOUT": 3
}

reverse_label_map = {
    v: k for k, v in label_map.items()
}

y = y.map(label_map)

# ----------------------------------
# TRAIN TEST SPLIT
# ----------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))

# ----------------------------------
# TRAIN MODEL
# ----------------------------------

model = XGBClassifier(
    objective="multi:softmax",
    num_class=4,
    random_state=42,
    n_estimators=100,
    max_depth=4
)

model.fit(X_train, y_train)

# ----------------------------------
# PREDICT
# ----------------------------------

# ----------------------------------
# TEST SET PREDICTIONS (for evaluation)
# ----------------------------------

predictions = model.predict(X_test)

# ==================================
# SAVE PREDICTIONS FOR ALL ROWS
# ==================================

all_predictions = model.predict(X)

all_probabilities = model.predict_proba(X)

prediction_df = pd.DataFrame({
    "checkout_id": df["checkout_id"],
    "predicted_cause": [
        reverse_label_map[p]
        for p in all_predictions
    ],
    "prediction_confidence":
        all_probabilities.max(axis=1)
})

prediction_df.to_csv(
    "data/root_cause_predictions.csv",
    index=False
)

print(
    "Saved predictions:",
    len(prediction_df)
)

# ----------------------------------
# EVALUATE
# ----------------------------------

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\nAccuracy")
print(accuracy)

cm = confusion_matrix(
    y_test,
    predictions
)

print("\nConfusion Matrix")
print(cm)

print("\nClassification Report")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "PRICE_HESITATION",
            "PAYMENT_FAILURE",
            "OTP_FRICTION",
            "DISTRACTION_TIMEOUT"
        ]
    )
)
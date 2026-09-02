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

# Save feature names before train/test split
feature_names = X.columns

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
# FEATURE IMPORTANCE
# ----------------------------------

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": model.feature_importances_
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

print("\n" + "=" * 60)
print("TOP 20 FEATURES")
print("=" * 60)

print(
    importance_df.head(20).to_string(index=False)
)

# ----------------------------------
# PREDICT
# ----------------------------------

predictions = model.predict(X_test)

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

# ----------------------------------
# OPTIONAL: TOP 10 ONLY
# ----------------------------------

print("\nTop 10 Most Important Features")

for _, row in importance_df.head(20).iterrows():
    print(
        f"{row['feature']:<40} "
        f"{row['importance']:.4f}"
    )
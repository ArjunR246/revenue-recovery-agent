import sqlite3
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    brier_score_loss
)
from sklearn.calibration import calibration_curve

from xgboost import XGBClassifier


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

print("Rows loaded:", len(df))


# ==========================================
# FEATURES
# ==========================================

feature_columns = [

    "amount",
    "session_duration_seconds",
    "inactivity_seconds",
    "retry_count",
    "otp_attempts",
    "minutes_since_dropoff",

    "dropoff_cause",
    "payment_method",
    "device_type",
    "network_quality",

    "upi_collect_expired"
]

target_column = "was_recovered"

X = df[feature_columns].copy()
y = df[target_column]


# ==========================================
# ONE HOT ENCODING
# ==========================================

X = pd.get_dummies(
    X,
    drop_first=False
)

print(
    "Feature count after encoding:",
    X.shape[1]
)


# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


# ==========================================
# MODEL
# ==========================================

model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss"
)

model.fit(
    X_train,
    y_train
)


# ==========================================
# PREDICTIONS
# ==========================================

y_prob = model.predict_proba(
    X_test
)[:, 1]

y_pred = model.predict(
    X_test
)


# ==========================================
# ROC AUC
# ==========================================

auc = roc_auc_score(
    y_test,
    y_prob
)

print("\nROC AUC")
print(round(auc, 4))


# ==========================================
# BRIER SCORE
# ==========================================

brier = brier_score_loss(
    y_test,
    y_prob
)

print("\nBrier Score")
print(round(brier, 4))


# ==========================================
# CALIBRATION TABLE
# ==========================================

fraction_pos, mean_pred = calibration_curve(
    y_test,
    y_prob,
    n_bins=10,
    strategy="uniform"
)

calibration_df = pd.DataFrame({
    "mean_predicted_probability": mean_pred,
    "actual_recovery_rate": fraction_pos
})

print("\nCalibration Table")
print(calibration_df)


# ==========================================
# ROOT CAUSE COMPARISON
# ==========================================

test_index = X_test.index

comparison = pd.DataFrame({

    "root_cause":
        df.loc[
            test_index,
            "dropoff_cause"
        ].values,

    "predicted_score":
        y_prob,

    "actual":
        y_test.values
})

summary = (
    comparison
    .groupby("root_cause")
    .agg(
        avg_predicted_score=(
            "predicted_score",
            "mean"
        ),
        actual_recovery_rate=(
            "actual",
            "mean"
        ),
        rows=(
            "actual",
            "count"
        )
    )
)

print("\nRoot Cause Comparison")
print(summary)


# ==========================================
# FEATURE IMPORTANCE
# ==========================================

importance_df = pd.DataFrame({

    "feature": X.columns,

    "importance":
        model.feature_importances_

})

importance_df = (
    importance_df
    .sort_values(
        "importance",
        ascending=False
    )
)

print("\nTop 15 Features")
print(
    importance_df.head(15)
)
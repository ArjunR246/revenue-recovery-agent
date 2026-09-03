import sqlite3
import pandas as pd
import numpy as np

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, brier_score_loss
from xgboost import XGBClassifier


# ============================================================
# Load data
# ============================================================

conn = sqlite3.connect("data/revenue_recovery.db")

df = pd.read_sql(
    "SELECT * FROM checkouts",
    conn
)

conn.close()

print(f"Rows loaded: {len(df)}")


# ============================================================
# Define features and target
# ============================================================

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
    "upi_collect_expired",
]

target_column = "was_recovered"

X = df[feature_columns].copy()
y = df[target_column].copy()

X = pd.get_dummies(
    X,
    drop_first=False
)

print(f"Feature count after encoding: {X.shape[1]}")


# ============================================================
# 5-fold cross-validation
# ============================================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)


roc_auc_scores = []
brier_scores = []


for fold_number, (train_idx, test_idx) in enumerate(
    cv.split(X, y),
    start=1
):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    # --------------------------------------------------------
    # Create fresh model for this fold
    # --------------------------------------------------------

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss",
    )

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # Probability predictions
    # --------------------------------------------------------

    y_prob = model.predict_proba(
        X_test
    )[:, 1]

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    fold_auc = roc_auc_score(
        y_test,
        y_prob
    )

    fold_brier = brier_score_loss(
        y_test,
        y_prob
    )

    roc_auc_scores.append(fold_auc)
    brier_scores.append(fold_brier)

    print(
        f"\nFold {fold_number}"
    )

    print(
        f"ROC AUC:     {fold_auc:.4f}"
    )

    print(
        f"Brier Score: {fold_brier:.4f}"
    )


# ============================================================
# Aggregate metrics
# ============================================================

roc_auc_scores = np.array(
    roc_auc_scores
)

brier_scores = np.array(
    brier_scores
)


print("\n5-Fold Cross-Validation")
print("-" * 30)

print("\nROC AUC by fold")

for i, score in enumerate(
    roc_auc_scores,
    start=1
):
    print(
        f"Fold {i}: {score:.4f}"
    )

print(
    f"\nMean ROC AUC: "
    f"{roc_auc_scores.mean():.4f}"
)

print(
    f"Std ROC AUC:  "
    f"{roc_auc_scores.std():.4f}"
)


print("\nBrier Score by fold")

for i, score in enumerate(
    brier_scores,
    start=1
):
    print(
        f"Fold {i}: {score:.4f}"
    )

print(
    f"\nMean Brier Score: "
    f"{brier_scores.mean():.4f}"
)

print(
    f"Std Brier Score:  "
    f"{brier_scores.std():.4f}"
)


# ============================================================
# Baseline comparison
# ============================================================

baseline_brier = 0.2103

improvement = (
    baseline_brier -
    brier_scores.mean()
)

relative_improvement = (
    improvement /
    baseline_brier
) * 100


print("\nBaseline Comparison")
print("-" * 30)

print(
    f"Naive baseline Brier: "
    f"{baseline_brier:.4f}"
)

print(
    f"ML mean Brier:        "
    f"{brier_scores.mean():.4f}"
)

print(
    f"Absolute improvement: "
    f"{improvement:.4f}"
)

print(
    f"Relative improvement: "
    f"{relative_improvement:.2f}%"
)


# ============================================================
# Duplicate-row check
# ============================================================

duplicate_count = df.duplicated().sum()

print("\nDuplicate Check")
print("-" * 30)

print(
    f"Exact duplicate rows: "
    f"{duplicate_count}"
)

print(
    f"Duplicate percentage: "
    f"{duplicate_count / len(df) * 100:.2f}%"
)


# ============================================================
# Ground-truth leakage check
# ============================================================

print("\nLeakage Check")
print("-" * 30)

if "recovery_probability_ground_truth" in X.columns:

    print(
        "WARNING: recovery_probability_ground_truth "
        "is present as a model feature."
    )

else:

    print(
        "PASS: recovery_probability_ground_truth "
        "is NOT a model feature."
    )


# ============================================================
# Feature-signature check
# ============================================================

feature_signature = X.astype(str).agg(
    "|".join,
    axis=1
)

duplicate_signatures = (
    feature_signature.duplicated().sum()
)

print("\nFeature Signature Check")
print("-" * 30)

print(
    f"Duplicate feature signatures: "
    f"{duplicate_signatures}"
)


# ============================================================
# Final verdict
# ============================================================

print("\nValidation Verdict")
print("-" * 30)

if (
    brier_scores.mean() < baseline_brier
    and relative_improvement >= 5
    and duplicate_count == 0
    and "recovery_probability_ground_truth" not in X.columns
):

    print(
        "PASS: Stage 4B recoverability model "
        "is ready to freeze."
    )

else:

    print(
        "REVIEW: Stage 4B needs additional investigation."
    )
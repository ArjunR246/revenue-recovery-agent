import pandas as pd
import numpy as np

np.random.seed(42)

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    "data/routing_decisions.csv"
)

print(
    f"Rows loaded: {len(df)}"
)

# ============================================================
# NAIVE BASELINE
# ============================================================
#
# Strategy:
#
# Nudge everyone.
#
# Recovery probability =
# recoverability_score
#
# No routing.
# No stopping rules.
# No decay-aware optimization.
#
# ============================================================

baseline_records = []

recovered_revenue = 0

for _, row in df.iterrows():

    recovered = np.random.binomial(
        1,
        row["recoverability_score"]
    )

    outcome = (
        "RECOVERED"
        if recovered
        else "PENDING"
    )

    if recovered:
        recovered_revenue += row["amount"]

    baseline_records.append({

        "checkout_id":
        row["checkout_id"],

        "action":
        "NUDGE",

        "recoverability_score":
        row["recoverability_score"],

        "amount":
        row["amount"],

        "outcome":
        outcome
    })

baseline_df = pd.DataFrame(
    baseline_records
)

# ============================================================
# METRICS
# ============================================================

total_revenue = (
    df["amount"]
    .sum()
)

recovered_count = (
    baseline_df["outcome"]
    ==
    "RECOVERED"
).sum()

recovery_rate = (
    recovered_count
    /
    len(baseline_df)
    *
    100
)

touches_per_recovery = (
    len(baseline_df)
    /
    max(recovered_count, 1)
)

metrics_df = pd.DataFrame([{

    "strategy":
    "BASELINE",

    "at_risk_revenue":
    total_revenue,

    "recovered_revenue":
    recovered_revenue,

    "recovery_rate":
    recovery_rate,

    "touches_per_recovery":
    touches_per_recovery,

    "total_checkouts":
    len(df)
}])

# ============================================================
# SAVE
# ============================================================

baseline_df.to_csv(
    "data/baseline_results.csv",
    index=False
)

metrics_df.to_csv(
    "data/baseline_metrics.csv",
    index=False
)

# ============================================================
# OUTPUT
# ============================================================

print(
    "\nBASELINE RESULTS"
)

print(
    metrics_df.to_string(
        index=False
    )
)

print(
    "\nSaved:"
)

print(
    "data/baseline_results.csv"
)

print(
    "data/baseline_metrics.csv"
)
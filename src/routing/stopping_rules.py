import sqlite3
import pandas as pd
import numpy as np

# ============================================================
# GLOBAL CONSTANTS
# ============================================================

MAX_TOUCHES = 3

COOLDOWN_MINUTES = 360

HARD_EXPIRY_MINUTES = 4320

# Based on Stage 5 floors:
#
# OTP_FRICTION       C = 0.3635
# PAYMENT_FAILURE    C = 0.2977
# DISTRACTION        C = 0.2100
# PRICE_HESITATION   C = 0.1080
#
# Use a conservative global threshold.
#
MIN_RECOVERABILITY = 0.20

MAX_CONSECUTIVE_IGNORES = 2

np.random.seed(42)

# ============================================================
# LOAD CHECKOUTS
# ============================================================

conn = sqlite3.connect(
    "data/revenue_recovery.db"
)

df = pd.read_sql(
    "SELECT * FROM checkouts",
    conn
)

conn.close()

print(
    f"Rows loaded: {len(df)}"
)

# ============================================================
# SIMULATED HISTORY
# ============================================================
#
# For demo purposes.
#
# Later this can be replaced by a real
# interventions table lookup.
#
# ============================================================

df["touch_count"] = np.random.choice(
    [0, 1, 2, 3, 4],
    size=len(df),
    p=[0.45, 0.25, 0.15, 0.10, 0.05]
)

df["minutes_since_last_intervention"] = np.random.randint(
    0,
    1000,
    size=len(df)
)

df["consecutive_ignored_interventions"] = np.random.choice(
    [0, 1, 2, 3],
    size=len(df),
    p=[0.50, 0.25, 0.15, 0.10]
)

df["opt_out_flag"] = np.random.choice(
    [False, True],
    size=len(df),
    p=[0.97, 0.03]
)

# ============================================================
# RECOVERABILITY APPROXIMATION
# ============================================================
#
# For Stage 7 only.
#
# We need a recoverability score to evaluate
# stopping logic before routing.
#
# Use the hidden ground-truth probability as
# a stand-in for the already-trained scorer.
#
# Later:
#
# replace with model.predict_proba(...)
#
# ============================================================

df["recoverability_score"] = (
    df["recovery_probability_ground_truth"]
)

# ============================================================
# STOPPING RULES
# ============================================================

def evaluate_stopping_rules(row):

    # ----------------------------------------
    # hard expiry
    # ----------------------------------------

    if (
        row["minutes_since_dropoff"]
        >= HARD_EXPIRY_MINUTES
    ):
        return pd.Series({
            "decision": "STOP",
            "stop_reason": "HARD_EXPIRY"
        })

    # ----------------------------------------
    # opt out
    # ----------------------------------------

    if row["opt_out_flag"]:

        return pd.Series({
            "decision": "STOP",
            "stop_reason": "OPT_OUT"
        })

    # ----------------------------------------
    # max touches
    # ----------------------------------------

    if (
        row["touch_count"]
        >= MAX_TOUCHES
    ):
        return pd.Series({
            "decision": "STOP",
            "stop_reason": "MAX_TOUCHES"
        })

    # ----------------------------------------
    # cooldown
    # ----------------------------------------

    if (
        row["touch_count"] > 0
        and
        row["minutes_since_last_intervention"]
        < COOLDOWN_MINUTES
    ):
        return pd.Series({
            "decision": "STOP",
            "stop_reason": "COOLDOWN"
        })

    # ----------------------------------------
    # ignored interventions
    # ----------------------------------------

    if (
        row["consecutive_ignored_interventions"]
        >= MAX_CONSECUTIVE_IGNORES
    ):
        return pd.Series({
            "decision": "STOP",
            "stop_reason": "IGNORED_INTERVENTIONS"
        })

    # ----------------------------------------
    # recoverability floor
    # ----------------------------------------

    if (
        row["recoverability_score"]
        < MIN_RECOVERABILITY
    ):
        return pd.Series({
            "decision": "STOP",
            "stop_reason": "LOW_RECOVERABILITY"
        })

    # ----------------------------------------
    # continue
    # ----------------------------------------

    return pd.Series({
        "decision": "CONTINUE",
        "stop_reason": "NONE"
    })

# ============================================================
# RUN
# ============================================================

results = df.apply(
    evaluate_stopping_rules,
    axis=1
)

df = pd.concat(
    [df, results],
    axis=1
)

# ============================================================
# DISTRIBUTION
# ============================================================

print(
    "\n"
    + "=" * 60
)

print(
    "STOPPING RULE RESULTS"
)

print(
    "=" * 60
)

print(
    df["decision"]
    .value_counts()
)

print(
    "\n"
    + "=" * 60
)

print(
    "STOP REASONS"
)

print(
    "=" * 60
)

print(
    df["stop_reason"]
    .value_counts()
)

# ============================================================
# SAMPLE
# ============================================================

print(
    "\n"
    + "=" * 60
)

print(
    "SAMPLE OUTPUT"
)

print(
    "=" * 60
)

sample = df[
    [
        "checkout_id",
        "touch_count",
        "minutes_since_last_intervention",
        "consecutive_ignored_interventions",
        "opt_out_flag",
        "recoverability_score",
        "decision",
        "stop_reason"
    ]
].sample(
    15,
    random_state=42
)

print(
    sample.to_string(
        index=False
    )
)

# ============================================================
# SAVE
# ============================================================

output_path = (
    "data/stopping_rule_results.csv"
)

df.to_csv(
    output_path,
    index=False
)

print(
    f"\nSaved to {output_path}"
)
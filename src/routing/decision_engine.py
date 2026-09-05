import sqlite3
import pandas as pd
import numpy as np

stops = pd.read_csv(
    "data/stopping_rule_results.csv"
)

stop_lookup = dict(
    zip(
        stops["checkout_id"],
        stops["decision"]
    )
)

reason_lookup = dict(
    zip(
        stops["checkout_id"],
        stops["stop_reason"]
    )
)

# ============================================================
# DECAY PARAMETERS FROM STAGE 5B
# ============================================================

DECAY_PARAMS = {
    "OTP_FRICTION": {
        "A": 0.2424,
        "k": 0.001232,
        "C": 0.3635,
        "window_minutes": 2432
    },
    "PAYMENT_FAILURE": {
        "A": 0.1862,
        "k": 0.001026,
        "C": 0.2977,
        "window_minutes": 2920
    },
    "DISTRACTION_TIMEOUT": {
        "A": 0.2324,
        "k": 0.001017,
        "C": 0.2100,
        "window_minutes": 2946
    },
    "PRICE_HESITATION": {
        "A": 0.1292,
        "k": 0.000375,
        "C": 0.1080,
        "window_minutes": 4320
    }
}

# ============================================================
# ACTION COSTS
# ============================================================

ACTION_COSTS = {
    "RETRY_LINK": 0.98,
    "PAYMENT_METHOD_SWITCH": 0.95,
    "NUDGE": 0.92,
    "DISCOUNT_OFFER": 0.85,
    "HUMAN_ESCALATION": 0.80,
    "STOP": 0.00
}

# ============================================================
# VALID ACTIONS BY ROOT CAUSE
# ============================================================

VALID_ACTIONS = {
    "OTP_FRICTION": [
        "RETRY_LINK",
        "NUDGE",
        "STOP"
    ],
    "PAYMENT_FAILURE": [
        "PAYMENT_METHOD_SWITCH",
        "RETRY_LINK",
        "NUDGE",
        "STOP"
    ],
    "DISTRACTION_TIMEOUT": [
        "NUDGE",
        "STOP"
    ],
    "PRICE_HESITATION": [
        "DISCOUNT_OFFER",
        "NUDGE",
        "HUMAN_ESCALATION",
        "STOP"
    ]
}

# ============================================================
# LOAD DATA
# ============================================================

conn = sqlite3.connect(
    "data/revenue_recovery.db"
)

df = pd.read_sql(
    "SELECT * FROM checkouts",
    conn
)

conn.close()

# ==========================================
# LOAD CLASSIFIER PREDICTIONS
# ==========================================

predictions = pd.read_csv(
    "data/root_cause_predictions.csv"
)

print(
    f"Prediction rows: {len(predictions)}"
)

df = df.merge(
    predictions,
    on="checkout_id",
    how="left"
)

print(
    f"Rows loaded: {len(df)}"
)

print("\nColumns:")
print(df.columns.tolist())

# ============================================================
# RECOVERABILITY CURVE
# ============================================================

def recoverability_at_time(
    cause,
    minutes_since_dropoff
):

    p = DECAY_PARAMS[cause]

    score = (
        p["A"]
        * np.exp(
            -p["k"]
            * minutes_since_dropoff
        )
        + p["C"]
    )

    return float(
        np.clip(score, 0, 1)
    )

# ============================================================
# ERV
# ============================================================

def calculate_erv(
    recoverability,
    amount,
    action
):

    return (
        recoverability
        * amount
        * ACTION_COSTS[action]
    )

# ============================================================
# ROUTER
# ============================================================

def choose_action(row):
    if stop_lookup.get(
        row["checkout_id"]
    ) == "STOP":

        return pd.Series({
            "chosen_action": "STOP",
            "ERV_score": 0,

            "prediction_confidence":
            round(
                row["prediction_confidence"],
                4
            ),

            "explanation":
            f"Stopped by rule: "
            f"{reason_lookup[row['checkout_id']]}"
        })

    cause = row["predicted_cause"]

    amount = row["amount"]

    minutes = row["minutes_since_dropoff"]

    retry_count = row["retry_count"]

    params = DECAY_PARAMS[cause]

    # ----------------------------------------
    # intervention window expired
    # ----------------------------------------

    if minutes > params["window_minutes"]:

        return pd.Series({
            "chosen_action": "STOP",
            "ERV_score": 0,

            "prediction_confidence":
            round(
                row["prediction_confidence"],
                4
            ),

            "explanation":
            (
                f"STOP chosen: "
                f"{minutes} min exceeds "
                f"{params['window_minutes']} min "
                f"window for {cause}"
            )
        })

    recoverability = recoverability_at_time(
        cause,
        minutes
    )

    candidate_actions = (
        VALID_ACTIONS[cause]
    )

    ervs = {}

    for action in candidate_actions:
        if action == "DISCOUNT_OFFER":

            if amount < 7000:
                continue

            if recoverability < 0.20:
                continue
        # -------------------------
        # escalation only for
        # large carts
        # -------------------------

        if action == "HUMAN_ESCALATION":

            if amount < 8000:
                continue

            if recoverability < 0.25:
                continue

        # -------------------------
        # retry link only after
        # at least one retry
        # -------------------------

        if (
            action == "RETRY_LINK"
            and retry_count == 0
        ):
            continue

        erv = calculate_erv(
            recoverability,
            amount,
            action
        )

        # --------------------------------
        # action effectiveness bonus
        # --------------------------------

        if (
            cause == "OTP_FRICTION"
            and action == "RETRY_LINK"
        ):
            erv *= 1.15

        elif (
            cause == "PAYMENT_FAILURE"
            and action == "PAYMENT_METHOD_SWITCH"
        ):
            erv *= 1.20

        elif (
            cause == "PRICE_HESITATION"
            and action == "DISCOUNT_OFFER"
        ):
            erv *= 1.25

        elif (
            cause == "DISTRACTION_TIMEOUT"
            and action == "NUDGE"
        ):
            erv *= 1.15

        ervs[action] = erv

    if len(ervs) == 0:

        return pd.Series({
            "chosen_action": "STOP",
            "ERV_score": 0,

            "prediction_confidence":
            round(
                row["prediction_confidence"],
                4
            ),

            "explanation":
            "No viable intervention"
        })

    best_action = max(
        ervs,
        key=ervs.get
    )

    best_erv = ervs[
        best_action
    ]

    confidence = row["prediction_confidence"]

    explanation = (
        f"{best_action} chosen | "
        f"cause={cause} | "
        f"confidence={confidence:.3f} | "
        f"recoverability={recoverability:.3f} | "
        f"time={minutes}min | "
        f"amount=₹{amount:.0f} | "
        f"ERV=₹{best_erv:.0f}"
    )

    return pd.Series({
        "chosen_action":
        best_action,

        "ERV_score":
        round(best_erv, 2),

        "prediction_confidence":
        round(
            row["prediction_confidence"],
            4
        ),

        "explanation":
        explanation
    })

# ============================================================
# RUN ROUTER
# ============================================================

routing_output = df.apply(
    choose_action,
    axis=1
)

df = pd.concat(
    [
        df,
        routing_output
    ],
    axis=1
)

# ============================================================
# RECOVERABILITY SCORE
# ============================================================

df["recoverability_score"] = df.apply(
    lambda row: recoverability_at_time(
        row["predicted_cause"],
        row["minutes_since_dropoff"]
    ),
    axis=1
)

# ============================================================
# ACTION DISTRIBUTION
# ============================================================

print(
    "\n"
    + "=" * 60
)

print(
    "ACTION DISTRIBUTION"
)

print(
    "=" * 60
)

print(
    df["chosen_action"]
    .value_counts()
)

# ============================================================
# SAMPLE OUTPUT
# ============================================================

print(
    "\n"
    + "=" * 60
)

print(
    "SAMPLE DECISIONS"
)

print(
    "=" * 60
)

sample = df[
    [
        "checkout_id",
        "dropoff_cause",
        "amount",
        "minutes_since_dropoff",
        "chosen_action",
        "ERV_score",
        "explanation"
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
    "data/routing_decisions.csv"
)

df.to_csv(
    output_path,
    index=False
)

print(
    f"\nSaved to {output_path}"
)
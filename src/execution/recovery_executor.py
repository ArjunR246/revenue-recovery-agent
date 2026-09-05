import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

np.random.seed(42)

# ============================================================
# LOAD ROUTING OUTPUT
# ============================================================

df = pd.read_csv(
    "data/routing_decisions.csv"
)

print(
    f"Rows loaded: {len(df)}"
)

# ============================================================
# EXECUTION HELPERS
# ============================================================

def build_retry_link_payload(checkout_id, amount):

    return {
        "type": "link",
        "amount": int(amount * 100),
        "currency": "INR",
        "reference_id": checkout_id,
        "description": "Checkout recovery payment link"
    }


def choose_alternate_method(current_method):

    methods = [
        "UPI",
        "CARD",
        "WALLET"
    ]

    methods = [
        m
        for m in methods
        if m != current_method
    ]

    return np.random.choice(
        methods
    )


def build_nudge_payload(checkout_id):

    return {
        "channel": "sms",
        "checkout_id": checkout_id,
        "message":
        (
            "Complete your checkout. "
            "Your order is waiting."
        )
    }


def build_discount_payload(amount):

    discount_pct = 10

    return {
        "coupon_code":
        f"SAVE10",
        "discount_percent":
        discount_pct,
        "discount_value":
        round(
            amount * 0.10,
            2
        )
    }

# ============================================================
# EXECUTOR
# ============================================================

execution_records = []

audit_records = []

total_recovered_revenue = 0

for _, row in df.iterrows():

    action = row["chosen_action"]

    checkout_id = row["checkout_id"]

    amount = row["amount"]

    recoverability = row[
        "recoverability_score"
    ]

    payload = None

    execution_status = (
        "NO_ACTION"
    )

    # ----------------------------------------
    # STOP
    # ----------------------------------------

    if action == "STOP":

        execution_status = (
            "SKIPPED"
        )

    # ----------------------------------------
    # RETRY LINK
    # ----------------------------------------

    elif action == "RETRY_LINK":

        payload = (
            build_retry_link_payload(
                checkout_id,
                amount
            )
        )

        execution_status = (
            "RETRY_SENT"
        )

    # ----------------------------------------
    # PAYMENT METHOD SWITCH
    # ----------------------------------------

    elif (
        action
        ==
        "PAYMENT_METHOD_SWITCH"
    ):

        payload = {
            "suggested_method":
            choose_alternate_method(
                row["payment_method"]
            )
        }

        execution_status = (
            "METHOD_SWITCH_SENT"
        )

    # ----------------------------------------
    # NUDGE
    # ----------------------------------------

    elif action == "NUDGE":

        payload = (
            build_nudge_payload(
                checkout_id
            )
        )

        execution_status = (
            "NUDGE_SENT"
        )

    # ----------------------------------------
    # DISCOUNT
    # ----------------------------------------

    elif (
        action
        ==
        "DISCOUNT_OFFER"
    ):

        payload = (
            build_discount_payload(
                amount
            )
        )

        execution_status = (
            "DISCOUNT_SENT"
        )

    # ----------------------------------------
    # HUMAN ESCALATION
    # ----------------------------------------

    elif (
        action
        ==
        "HUMAN_ESCALATION"
    ):

        payload = {
            "ticket_priority":
            "HIGH"
        }

        execution_status = (
            "ESCALATED"
        )

    # ========================================================
    # SIMULATED OUTCOME
    # ========================================================

    if action == "STOP":

        simulated_outcome = (
            "NOT_CONTACTED"
        )

    else:

        recovered = np.random.binomial(
            1,
            recoverability
        )

        if recovered:

            simulated_outcome = (
                "RECOVERED"
            )

            total_recovered_revenue += (
                amount
            )

        else:

            simulated_outcome = (
                "PENDING"
            )

    # ========================================================
    # EXECUTION RECORD
    # ========================================================

    execution_records.append({

        "checkout_id":
        checkout_id,

        "action":
        action,

        "execution_status":
        execution_status,

        "payload":
        str(payload),

        "simulated_outcome":
        simulated_outcome
    })

    # ========================================================
    # AUDIT RECORD
    # ========================================================

    audit_records.append({

        "timestamp":
        datetime.utcnow(),

        "checkout_id":
        checkout_id,

        "amount": amount,

        "predicted_cause":
        row["predicted_cause"],

        "confidence": 
        round(
            row["prediction_confidence"],
            4
        ),

        "recoverability_score":
        round(
            recoverability,
            4
        ),

        "chosen_action":
        action,

        "ERV_score":
        row["ERV_score"],

        "reasoning":
        row["explanation"],

        "stop_reason":
        row.get("stop_reason", "NONE"),

        "simulated_outcome":
        simulated_outcome
    })

# ============================================================
# SAVE
# ============================================================

execution_df = pd.DataFrame(
    execution_records
)

audit_df = pd.DataFrame(
    audit_records
)

execution_df.to_csv(
    "data/executed_interventions.csv",
    index=False
)

audit_df.to_csv(
    "data/audit_logs.csv",
    index=False
)
print(
    "data/ai_metrics.csv"
)
total_at_risk = (
    df["amount"]
    .sum()
)
# ============================================================
# AI METRICS
# ============================================================

total_checkouts = len(df)

successful_recoveries = len(
    audit_df[
        audit_df["simulated_outcome"]
        == "RECOVERED"
    ]
)

total_touches = len(
    audit_df[
        audit_df["chosen_action"]
        != "STOP"
    ]
)

recovery_rate = (
    total_recovered_revenue
    / total_at_risk
)

touches_per_recovery = (
    total_touches
    / successful_recoveries
    if successful_recoveries > 0
    else 0
)

ai_metrics = pd.DataFrame([{

    "strategy":
        "AI_AGENT",

    "at_risk_revenue":
        total_at_risk,

    "recovered_revenue":
        total_recovered_revenue,

    "recovery_rate":
        round(
            recovery_rate,
            4
        ),

    "touches_per_recovery":
        round(
            touches_per_recovery,
            2
        ),

    "total_checkouts":
        total_checkouts
}])

ai_metrics.to_csv(
    "data/ai_metrics.csv",
    index=False
)

print(
    "\nSaved: data/ai_metrics.csv"
)
# ============================================================
# SUMMARY
# ============================================================



print(
    "\n"
    + "=" * 60
)

print(
    "RECOVERY SUMMARY"
)

print(
    "=" * 60
)

print(
    f"At-risk revenue: "
    f"₹{total_at_risk:,.0f}"
)

print(
    f"Recovered revenue: "
    f"₹{total_recovered_revenue:,.0f}"
)

print(
    f"Recovery rate: "
    f"{100 * total_recovered_revenue / total_at_risk:.2f}%"
)
# ============================================================
# CONTACTED RECOVERY RATE
# ============================================================

contacted = audit_df[
    audit_df["simulated_outcome"]
    !=
    "NOT_CONTACTED"
]

contacted_recovered = contacted[
    contacted["simulated_outcome"]
    ==
    "RECOVERED"
]

contacted_rate = (
    len(contacted_recovered)
    /
    len(contacted)
    *
    100
)

print(
    f"Contacted recovery rate: "
    f"{contacted_rate:.2f}%"
)

# ============================================================
# STOP REASON BREAKDOWN
# ============================================================

print(
    "\n"
    + "=" * 60
)

print(
    "STOP REASON BREAKDOWN"
)

print(
    "=" * 60
)

stops = df[
    df["chosen_action"]
    ==
    "STOP"
]

stop_breakdown = (
    stops["explanation"]
    .value_counts()
)

print(
    stop_breakdown
)
# ============================================================
# SAMPLE AUDIT LOGS
# ============================================================

print(
    "\n"
    + "=" * 60
)

print(
    "SAMPLE AUDIT LOGS"
)

print(
    "=" * 60
)

print(
    audit_df.sample(
        6,
        random_state=42
    ).to_string(
        index=False
    )
)

print(
    "\nSaved:"
)

print(
    "data/executed_interventions.csv"
)

print(
    "data/audit_logs.csv"
)
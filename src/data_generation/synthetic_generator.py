import os
import numpy as np
import pandas as pd


# ============================================================
# Configuration
# ============================================================

NUM_ROWS = 10000
OUTPUT_PATH = "data/raw/synthetic_checkouts.csv"

np.random.seed(42)


# ============================================================
# Helper functions
# ============================================================

def generate_recovery_probability(
    root_cause,
    amount,
    retry_count,
    inactivity_seconds,
    otp_attempts,
    network_quality,
    minutes_since_dropoff,
    session_duration_seconds,
    failure_reason_code,
):
    """
    Generate the underlying probability that a dropped checkout
    will recover.

    This is intentionally stronger than the original version:
    behavioral features have clearer within-cause effects.

    IMPORTANT:
    This probability is a hidden simulation variable.
    It must NOT be used as a model feature later.
    """

    if root_cause == "OTP_FRICTION":

        # Base probability
        p_recovery = 0.48

        # More OTP attempts indicate stronger purchase intent.
        # Each additional attempt increases recoverability.
        p_recovery += min(otp_attempts, 4) * 0.07

        # Recency matters strongly.
        if minutes_since_dropoff <= 5:
            p_recovery += 0.18
        elif minutes_since_dropoff <= 15:
            p_recovery += 0.12
        elif minutes_since_dropoff <= 30:
            p_recovery += 0.06
        elif minutes_since_dropoff <= 60:
            p_recovery += 0.00
        elif minutes_since_dropoff <= 180:
            p_recovery -= 0.08
        elif minutes_since_dropoff <= 1440:
            p_recovery -= 0.18
        else:
            p_recovery -= 0.30

        # Poor network makes OTP completion harder.
        if network_quality == "Poor":
            p_recovery -= 0.08
        elif network_quality == "Good":
            p_recovery += 0.04

    elif root_cause == "PAYMENT_FAILURE":

        p_recovery = 0.50

        # Retry behavior is a strong intent signal.
        if retry_count == 1:
            p_recovery += 0.10
        elif retry_count >= 2:
            p_recovery += 0.18

        # Recent failures are more recoverable.
        if minutes_since_dropoff <= 15:
            p_recovery += 0.12
        elif minutes_since_dropoff <= 60:
            p_recovery += 0.06
        elif minutes_since_dropoff <= 180:
            p_recovery -= 0.04
        elif minutes_since_dropoff <= 1440:
            p_recovery -= 0.12
        else:
            p_recovery -= 0.22

        # High-value purchases are somewhat harder to recover.
        if amount > 10000:
            p_recovery -= 0.12
        elif amount > 5000:
            p_recovery -= 0.06

        # Gateway-related failures are more recoverable than
        # failures indicating lack of funds.
        if failure_reason_code == "GATEWAY_ERROR":
            p_recovery += 0.08
        elif failure_reason_code == "INSUFFICIENT_FUNDS":
            p_recovery -= 0.12

    elif root_cause == "PRICE_HESITATION":

        p_recovery = 0.30

        # Higher cart value increases price sensitivity.
        if amount > 10000:
            p_recovery -= 0.16
        elif amount > 5000:
            p_recovery -= 0.08

        # Longer sessions indicate stronger engagement.
        if session_duration_seconds >= 600:
            p_recovery += 0.12
        elif session_duration_seconds >= 400:
            p_recovery += 0.07
        elif session_duration_seconds >= 200:
            p_recovery += 0.03

        # A retry suggests continued purchase intent.
        if retry_count == 1:
            p_recovery += 0.08
        elif retry_count >= 2:
            p_recovery += 0.14

        # Recent dropoffs are easier to recover.
        if minutes_since_dropoff <= 15:
            p_recovery += 0.10
        elif minutes_since_dropoff <= 60:
            p_recovery += 0.05
        elif minutes_since_dropoff <= 180:
            p_recovery -= 0.02
        elif minutes_since_dropoff <= 1440:
            p_recovery -= 0.10
        else:
            p_recovery -= 0.18

    elif root_cause == "DISTRACTION_TIMEOUT":

        p_recovery = 0.42

        # Inactivity is the strongest behavioral signal here.
        if inactivity_seconds <= 80:
            p_recovery += 0.18
        elif inactivity_seconds <= 200:
            p_recovery += 0.10
        elif inactivity_seconds <= 400:
            p_recovery += 0.02
        elif inactivity_seconds <= 700:
            p_recovery -= 0.10
        else:
            p_recovery -= 0.20

        # Recency also matters.
        if minutes_since_dropoff <= 15:
            p_recovery += 0.12
        elif minutes_since_dropoff <= 60:
            p_recovery += 0.06
        elif minutes_since_dropoff <= 180:
            p_recovery -= 0.04
        elif minutes_since_dropoff <= 1440:
            p_recovery -= 0.14
        else:
            p_recovery -= 0.25

        # Longer sessions indicate engagement before distraction.
        if session_duration_seconds >= 500:
            p_recovery += 0.10
        elif session_duration_seconds >= 300:
            p_recovery += 0.05

        # Occasional retry behavior still provides a small intent signal.
        if retry_count >= 1:
            p_recovery += 0.05

    # --------------------------------------------------------
    # Small amount of random variation
    # --------------------------------------------------------
    #
    # Keep the dataset probabilistic rather than deterministic,
    # but substantially lower the noise than before.
    #
    p_recovery += np.random.normal(0, 0.02)

    # Keep probabilities valid and prevent extreme certainty.
    p_recovery = np.clip(p_recovery, 0.02, 0.98)

    return p_recovery


# ============================================================
# Generate checkout data
# ============================================================

rows = []

payment_methods = ["UPI", "CARD", "WALLET"]
device_types = ["MOBILE", "DESKTOP"]
network_qualities = ["Good", "Average", "Poor"]

causes = [
    "PRICE_HESITATION",
    "PAYMENT_FAILURE",
    "OTP_FRICTION",
    "DISTRACTION_TIMEOUT",
]


for i in range(NUM_ROWS):

    checkout_id = f"CHK_{i + 1:06d}"

    timestamp = pd.Timestamp("2026-01-01") + pd.Timedelta(
        minutes=np.random.randint(0, 60 * 24 * 30)
    )

    root_cause = np.random.choice(causes)

    # --------------------------------------------------------
    # Cause-specific behavioral signals
    # --------------------------------------------------------

    if root_cause == "PRICE_HESITATION":

        amount = np.random.randint(2000, 15001)

        session_duration_seconds = np.random.choice(
            [np.random.randint(300, 901),
             np.random.randint(120, 301)],
            p=[0.75, 0.25],
        )

        inactivity_seconds = np.random.randint(20, 500)

        retry_count = np.random.choice(
            [0, 1, 2],
            p=[0.65, 0.25, 0.10],
        )

        otp_attempts = np.random.choice(
            [0, 1, 2],
            p=[0.75, 0.20, 0.05],
        )

        checkout_step_reached = "CART"

        payment_status = "ABANDONED"

        failure_reason_code = "NONE"

        upi_collect_expired = 0

    elif root_cause == "PAYMENT_FAILURE":

        amount = np.random.randint(500, 12001)

        session_duration_seconds = np.random.randint(120, 700)

        inactivity_seconds = np.random.randint(20, 500)

        retry_count = np.random.choice(
            [0, 1, 2, 3],
            p=[0.45, 0.30, 0.20, 0.05],
        )

        otp_attempts = np.random.choice(
            [0, 1, 2],
            p=[0.80, 0.15, 0.05],
        )

        checkout_step_reached = "PAYMENT"

        payment_status = "FAILED"

        failure_reason_code = np.random.choice(
            ["GATEWAY_ERROR", "INSUFFICIENT_FUNDS", "AUTH_TIMEOUT"],
            p=[0.45, 0.30, 0.25],
        )

        upi_collect_expired = int(
            failure_reason_code == "AUTH_TIMEOUT"
        )

    elif root_cause == "OTP_FRICTION":

        amount = np.random.randint(500, 10001)

        session_duration_seconds = np.random.randint(180, 800)

        inactivity_seconds = np.random.randint(20, 500)

        retry_count = np.random.choice(
            [0, 1, 2],
            p=[0.50, 0.30, 0.20],
        )

        otp_attempts = np.random.choice(
            [0, 1, 2, 3, 4],
            p=[0.05, 0.15, 0.25, 0.30, 0.25],
        )

        checkout_step_reached = "OTP"

        payment_status = "FAILED"

        failure_reason_code = "OTP_TIMEOUT"

        upi_collect_expired = 0

    else:  # DISTRACTION_TIMEOUT

        amount = np.random.randint(500, 9001)

        session_duration_seconds = np.random.randint(120, 700)

        inactivity_seconds = np.random.choice(
            [
                np.random.randint(200, 801),
                np.random.randint(80, 201),
                np.random.randint(0, 81),
            ],
            p=[0.70, 0.20, 0.10],
        )

        retry_count = np.random.choice(
            [0, 1, 2],
            p=[0.75, 0.20, 0.05],
        )

        otp_attempts = np.random.choice(
            [0, 1],
            p=[0.90, 0.10],
        )

        checkout_step_reached = "PAYMENT"

        payment_status = "ABANDONED"

        failure_reason_code = "NONE"

        upi_collect_expired = 0

    payment_method = np.random.choice(payment_methods)
    device_type = np.random.choice(device_types)
    network_quality = np.random.choice(
        network_qualities,
        p=[0.45, 0.40, 0.15],
    )

    # --------------------------------------------------------
    # Time since dropoff
    # --------------------------------------------------------

    minutes_since_dropoff = np.random.randint(5, 4321)

    # --------------------------------------------------------
    # Ground-truth recovery probability
    # --------------------------------------------------------

    recovery_probability = generate_recovery_probability(
        root_cause=root_cause,
        amount=amount,
        retry_count=retry_count,
        inactivity_seconds=inactivity_seconds,
        otp_attempts=otp_attempts,
        network_quality=network_quality,
        minutes_since_dropoff=minutes_since_dropoff,
        session_duration_seconds=session_duration_seconds,
        failure_reason_code=failure_reason_code,
    )

    # --------------------------------------------------------
    # Sample actual recovery outcome
    # --------------------------------------------------------

    was_recovered = np.random.binomial(
        1,
        recovery_probability,
    )

    # Keep legacy column synchronized.
    recovered = was_recovered

    # --------------------------------------------------------
    # Synthetic time-to-recovery
    # --------------------------------------------------------

    if was_recovered:
        time_to_recovery_minutes = np.random.randint(
            5,
            max(6, min(minutes_since_dropoff + 1, 1440)),
        )
    else:
        time_to_recovery_minutes = None

    rows.append({
        "checkout_id": checkout_id,
        "timestamp": timestamp,
        "amount": amount,
        "payment_method": payment_method,
        "device_type": device_type,
        "session_duration_seconds": session_duration_seconds,
        "inactivity_seconds": inactivity_seconds,
        "retry_count": retry_count,
        "checkout_step_reached": checkout_step_reached,
        "network_quality": network_quality,
        "payment_status": payment_status,
        "failure_reason_code": failure_reason_code,
        "otp_attempts": otp_attempts,
        "upi_collect_expired": upi_collect_expired,
        "dropoff_cause": root_cause,
        "recovered": recovered,
        "time_to_recovery_minutes": time_to_recovery_minutes,
        "minutes_since_dropoff": minutes_since_dropoff,
        "recovery_probability_ground_truth": round(
            float(recovery_probability),
            4,
        ),
        "was_recovered": was_recovered,
    })


# ============================================================
# Save dataset
# ============================================================

df = pd.DataFrame(rows)

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

df.to_csv(
    OUTPUT_PATH,
    index=False,
)

print(f"Generated {len(df)} checkout rows.")
print(f"Saved to: {OUTPUT_PATH}")

print("\nColumns:")
print(list(df.columns))

print("\nRecovery rate by root cause:")
print(
    df.groupby("dropoff_cause")["was_recovered"]
    .agg(["mean", "count"])
)

print("\nAverage hidden recovery probability by root cause:")
print(
    df.groupby("dropoff_cause")["recovery_probability_ground_truth"]
    .mean()
)
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

NUM_ROWS = 1000

np.random.seed(42)

data = []

for i in range(NUM_ROWS):
    checkout_id = f"CHK_{i+1:06d}"

    timestamp = datetime.now() - timedelta(
        minutes=np.random.randint(0, 10000)
    )

    cause = np.random.choice(
        [
            "PRICE_HESITATION",
            "PAYMENT_FAILURE",
            "OTP_FRICTION",
            "DISTRACTION_TIMEOUT"
        ]
    )

    # ----------------------------
    # PRICE HESITATION
    # ----------------------------

    if cause == "PRICE_HESITATION":

        amount = np.random.randint(5000, 15000)

        row = {
            "checkout_id": checkout_id,
            "timestamp": timestamp,
            "amount": amount,
            "payment_method": np.random.choice(
                ["UPI", "CARD", "NETBANKING"]
            ),
            "device_type": np.random.choice(
                ["Mobile", "Desktop"]
            ),
            "session_duration_seconds": np.random.randint(300, 900),
            "inactivity_seconds": np.random.randint(20, 120),
            "retry_count": np.random.randint(1, 4),
            "checkout_step_reached": "PAYMENT",
            "network_quality": np.random.choice(
                ["Good", "Average"]
            ),
            "payment_status": "ABANDONED",
            "failure_reason_code": "NONE",
            "otp_attempts": 0,
            "upi_collect_expired": False,
            "dropoff_cause": cause,
            "recovered": np.random.choice(
                [0, 1],
                p=[0.80, 0.20]
            ),
            "time_to_recovery_minutes": None
        }

    # ----------------------------
    # PAYMENT FAILURE
    # ----------------------------

    elif cause == "PAYMENT_FAILURE":

        row = {
            "checkout_id": checkout_id,
            "timestamp": timestamp,
            "amount": np.random.randint(500, 10000),
            "payment_method": np.random.choice(
                ["CARD", "NETBANKING"]
            ),
            "device_type": np.random.choice(
                ["Mobile", "Desktop"]
            ),
            "session_duration_seconds": np.random.randint(60, 300),
            "inactivity_seconds": np.random.randint(0, 60),
            "retry_count": np.random.randint(0, 2),
            "checkout_step_reached": "PAYMENT",
            "network_quality": np.random.choice(
                ["Good", "Average"]
            ),
            "payment_status": "FAILED",
            "failure_reason_code": np.random.choice(
                [
                    "BANK_DECLINED",
                    "INSUFFICIENT_FUNDS",
                    "GATEWAY_ERROR"
                ]
            ),
            "otp_attempts": 0,
            "upi_collect_expired": False,
            "dropoff_cause": cause,
            "recovered": np.random.choice(
                [0, 1],
                p=[0.45, 0.55]
            ),
            "time_to_recovery_minutes": None
        }

    # ----------------------------
    # OTP FRICTION
    # ----------------------------

    elif cause == "OTP_FRICTION":

        row = {
            "checkout_id": checkout_id,
            "timestamp": timestamp,
            "amount": np.random.randint(500, 8000),
            "payment_method": np.random.choice(
                ["UPI", "CARD"]
            ),
            "device_type": "Mobile",
            "session_duration_seconds": np.random.randint(120, 400),
            "inactivity_seconds": np.random.randint(20, 120),
            "retry_count": np.random.randint(1, 3),
            "checkout_step_reached": "OTP",
            "network_quality": np.random.choice(
                ["Average", "Poor"]
            ),
            "payment_status": "FAILED",
            "failure_reason_code": "OTP_TIMEOUT",
            "otp_attempts": np.random.randint(2, 5),
            "upi_collect_expired": np.random.choice(
                [True, False]
            ),
            "dropoff_cause": cause,
            "recovered": np.random.choice(
                [0, 1],
                p=[0.30, 0.70]
            ),
            "time_to_recovery_minutes": None
        }

    # ----------------------------
    # DISTRACTION TIMEOUT
    # ----------------------------

    else:

        row = {
            "checkout_id": checkout_id,
            "timestamp": timestamp,
            "amount": np.random.randint(500, 7000),
            "payment_method": np.random.choice(
                ["UPI", "CARD", "WALLET"]
            ),
            "device_type": np.random.choice(
                ["Mobile", "Desktop"]
            ),
            "session_duration_seconds": np.random.randint(30, 180),
            "inactivity_seconds": np.random.randint(200, 800),
            "retry_count": 0,
            "checkout_step_reached": np.random.choice(
                ["CART", "PAYMENT"]
            ),
            "network_quality": np.random.choice(
                ["Good", "Average", "Poor"]
            ),
            "payment_status": "ABANDONED",
            "failure_reason_code": "NONE",
            "otp_attempts": 0,
            "upi_collect_expired": False,
            "dropoff_cause": cause,
            "recovered": np.random.choice(
                [0, 1],
                p=[0.65, 0.35]
            ),
            "time_to_recovery_minutes": None
        }

    # Generate recovery time if recovered

    if row["recovered"] == 1:

        if cause == "OTP_FRICTION":
            row["time_to_recovery_minutes"] = np.random.randint(
                5, 60
            )

        elif cause == "PAYMENT_FAILURE":
            row["time_to_recovery_minutes"] = np.random.randint(
                15, 180
            )

        elif cause == "DISTRACTION_TIMEOUT":
            row["time_to_recovery_minutes"] = np.random.randint(
                30, 720
            )

        else:
            row["time_to_recovery_minutes"] = np.random.randint(
                1440, 4320
            )

    data.append(row)
df = pd.DataFrame(data)

output_path = "data/raw/synthetic_checkouts.csv"

df.to_csv(output_path, index=False)

print(f"Generated {len(df)} rows")
print(f"Saved to {output_path}")

print(df.head())
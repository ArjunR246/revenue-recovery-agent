import pandas as pd
import numpy as np
from datetime import datetime, timedelta

NUM_ROWS = 10000

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

    # ==================================================
    # PRICE HESITATION
    # ==================================================

    if cause == "PRICE_HESITATION":

        amount = np.random.randint(2000, 15000)

        if np.random.rand() < 0.75:
            session_duration = np.random.randint(300, 900)
        else:
            session_duration = np.random.randint(120, 300)

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
            "session_duration_seconds": session_duration,
            "inactivity_seconds": np.random.randint(20, 150),
            "retry_count": np.random.randint(1, 4),
            "checkout_step_reached": np.random.choice(
                ["PAYMENT", "OTP"],
                p=[0.90, 0.10]
            ),
            "network_quality": np.random.choice(
                ["Good", "Average"]
            ),
            "payment_status": "ABANDONED",
            "failure_reason_code": np.random.choice(
                ["NONE", "OTP_TIMEOUT"],
                p=[0.95, 0.05]
            ),
            "otp_attempts": np.random.choice(
                [0, 1, 2],
                p=[0.75, 0.20, 0.05]
            ),
            "upi_collect_expired": np.random.choice(
                [False, True],
                p=[0.95, 0.05]
            ),
            "dropoff_cause": cause,
            "recovered": np.random.choice(
                [0, 1],
                p=[0.80, 0.20]
            ),
            "time_to_recovery_minutes": None
        }

    # ==================================================
    # PAYMENT FAILURE
    # ==================================================

    elif cause == "PAYMENT_FAILURE":

        row = {
            "checkout_id": checkout_id,
            "timestamp": timestamp,
            "amount": np.random.randint(500, 12000),
            "payment_method": np.random.choice(
                ["CARD", "NETBANKING", "UPI"]
            ),
            "device_type": np.random.choice(
                ["Mobile", "Desktop"]
            ),
            "session_duration_seconds": np.random.randint(
                60, 350
            ),
            "inactivity_seconds": np.random.randint(
                0, 180
            ),
            "retry_count": np.random.randint(
                0, 3
            ),
            "checkout_step_reached": np.random.choice(
                ["PAYMENT", "OTP"],
                p=[0.85, 0.15]
            ),
            "network_quality": np.random.choice(
                ["Good", "Average", "Poor"],
                p=[0.50, 0.35, 0.15]
            ),
            "payment_status": "FAILED",
            "failure_reason_code": np.random.choice(
                [
                    "BANK_DECLINED",
                    "INSUFFICIENT_FUNDS",
                    "GATEWAY_ERROR",
                    "OTP_TIMEOUT"
                ],
                p=[0.35, 0.35, 0.25, 0.05]
            ),
            "otp_attempts": np.random.choice(
                [0, 1, 2],
                p=[0.80, 0.15, 0.05]
            ),
            "upi_collect_expired": np.random.choice(
                [False, True],
                p=[0.90, 0.10]
            ),
            "dropoff_cause": cause,
            "recovered": np.random.choice(
                [0, 1],
                p=[0.45, 0.55]
            ),
            "time_to_recovery_minutes": None
        }

    # ==================================================
    # OTP FRICTION
    # ==================================================

    elif cause == "OTP_FRICTION":

        if np.random.rand() < 0.80:
            otp_attempts = np.random.randint(2, 5)
        else:
            otp_attempts = np.random.randint(0, 2)

        row = {
            "checkout_id": checkout_id,
            "timestamp": timestamp,
            "amount": np.random.randint(500, 10000),
            "payment_method": np.random.choice(
                ["UPI", "CARD"]
            ),
            "device_type": np.random.choice(
                ["Mobile", "Desktop"],
                p=[0.85, 0.15]
            ),
            "session_duration_seconds": np.random.randint(
                100, 450
            ),
            "inactivity_seconds": np.random.randint(
                20, 180
            ),
            "retry_count": np.random.randint(
                1, 4
            ),
            "checkout_step_reached": np.random.choice(
                ["OTP", "PAYMENT"],
                p=[0.75, 0.25]
            ),
            "network_quality": np.random.choice(
                ["Average", "Poor", "Good"],
                p=[0.50, 0.30, 0.20]
            ),
            "payment_status": "FAILED",
            "failure_reason_code": np.random.choice(
                [
                    "OTP_TIMEOUT",
                    "UPI_EXPIRED",
                    "AUTH_TIMEOUT",
                    "NONE"
                ],
                p=[0.55, 0.20, 0.15, 0.10]
            ),
            "otp_attempts": otp_attempts,
            "upi_collect_expired": np.random.choice(
                [True, False],
                p=[0.60, 0.40]
            ),
            "dropoff_cause": cause,
            "recovered": np.random.choice(
                [0, 1],
                p=[0.30, 0.70]
            ),
            "time_to_recovery_minutes": None
        }

    # ==================================================
    # DISTRACTION TIMEOUT
    # ==================================================

    else:

        r = np.random.rand()

        if r < 0.70:
            inactivity = np.random.randint(
                200, 800
            )
        elif r < 0.90:
            inactivity = np.random.randint(
                80, 200
            )
        else:
            inactivity = np.random.randint(
                0, 80
            )

        row = {
            "checkout_id": checkout_id,
            "timestamp": timestamp,
            "amount": np.random.randint(500, 9000),
            "payment_method": np.random.choice(
                ["UPI", "CARD", "WALLET"]
            ),
            "device_type": np.random.choice(
                ["Mobile", "Desktop"]
            ),
            "session_duration_seconds": np.random.randint(
                30, 250
            ),
            "inactivity_seconds": inactivity,
            "retry_count": np.random.choice(
                [0, 1, 2],
                p=[0.75, 0.20, 0.05]
            ),
            "checkout_step_reached": np.random.choice(
                ["CART", "PAYMENT", "OTP"],
                p=[0.60, 0.30, 0.10]
            ),
            "network_quality": np.random.choice(
                ["Good", "Average", "Poor"]
            ),
            "payment_status": "ABANDONED",
            "failure_reason_code": np.random.choice(
                ["NONE", "OTP_TIMEOUT"],
                p=[0.95, 0.05]
            ),
            "otp_attempts": np.random.choice(
                [0, 1],
                p=[0.90, 0.10]
            ),
            "upi_collect_expired": np.random.choice(
                [False, True],
                p=[0.95, 0.05]
            ),
            "dropoff_cause": cause,
            "recovered": np.random.choice(
                [0, 1],
                p=[0.65, 0.35]
            ),
            "time_to_recovery_minutes": None
        }

    # ==================================================
    # RECOVERY TIME
    # ==================================================

    if row["recovered"] == 1:

        if cause == "OTP_FRICTION":

            row["time_to_recovery_minutes"] = (
                np.random.randint(5, 60)
            )

        elif cause == "PAYMENT_FAILURE":

            row["time_to_recovery_minutes"] = (
                np.random.randint(15, 180)
            )

        elif cause == "DISTRACTION_TIMEOUT":

            row["time_to_recovery_minutes"] = (
                np.random.randint(30, 720)
            )

        else:

            row["time_to_recovery_minutes"] = (
                np.random.randint(1440, 4320)
            )

    # ==================================================
    # LABEL NOISE (3%)
    # ==================================================

    if np.random.rand() < 0.03:

        row["dropoff_cause"] = np.random.choice(
            [
                "PRICE_HESITATION",
                "PAYMENT_FAILURE",
                "OTP_FRICTION",
                "DISTRACTION_TIMEOUT"
            ]
        )

    data.append(row)

df = pd.DataFrame(data)

output_path = "data/raw/synthetic_checkouts.csv"

df.to_csv(
    output_path,
    index=False
)

print(f"Generated {len(df)} rows")
print(f"Saved to {output_path}")

print(df.head())
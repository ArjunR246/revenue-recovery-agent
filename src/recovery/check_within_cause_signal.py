import sqlite3
import pandas as pd


DB_PATH = "data/revenue_recovery.db"


conn = sqlite3.connect(DB_PATH)

df = pd.read_sql(
    """
    SELECT
        dropoff_cause,
        otp_attempts,
        minutes_since_dropoff,
        retry_count,
        inactivity_seconds,
        was_recovered
    FROM checkouts
    """,
    conn,
)

conn.close()


# ============================================================
# 1. OTP friction: OTP attempts
# ============================================================

otp = df[
    df["dropoff_cause"] == "OTP_FRICTION"
].copy()

print("\n=== OTP_FRICTION: recovery by OTP attempts ===")

print(
    otp.groupby("otp_attempts")["was_recovered"]
    .agg(["mean", "count"])
    .rename(columns={
        "mean": "actual_recovery_rate",
        "count": "rows",
    })
)


# ============================================================
# 2. OTP friction: time since dropoff
# ============================================================

otp["time_bucket"] = pd.cut(
    otp["minutes_since_dropoff"],
    bins=[0, 15, 60, 180, 1440, float("inf")],
    labels=[
        "0-15 min",
        "16-60 min",
        "61-180 min",
        "181-1440 min",
        "1440+ min",
    ],
)

print("\n=== OTP_FRICTION: recovery by time since dropoff ===")

print(
    otp.groupby(
        "time_bucket",
        observed=False
    )["was_recovered"]
    .agg(["mean", "count"])
    .rename(columns={
        "mean": "actual_recovery_rate",
        "count": "rows",
    })
)


# ============================================================
# 3. Strong-good vs strong-bad OTP examples
# ============================================================

good_otp = otp[
    (otp["otp_attempts"] >= 3) &
    (otp["minutes_since_dropoff"] <= 15)
]

bad_otp = otp[
    (otp["otp_attempts"] <= 1) &
    (otp["minutes_since_dropoff"] >= 60)
]

print("\n=== OTP_FRICTION: good vs bad behavioral signals ===")

print(
    pd.DataFrame({
        "group": [
            "GOOD: 3+ OTP attempts + <=15 min",
            "BAD: <=1 OTP attempt + >=60 min",
        ],
        "actual_recovery_rate": [
            good_otp["was_recovered"].mean(),
            bad_otp["was_recovered"].mean(),
        ],
        "rows": [
            len(good_otp),
            len(bad_otp),
        ],
    })
)


# ============================================================
# 4. Distraction timeout: inactivity
# ============================================================

distraction = df[
    df["dropoff_cause"] == "DISTRACTION_TIMEOUT"
].copy()

distraction["inactivity_bucket"] = pd.cut(
    distraction["inactivity_seconds"],
    bins=[-1, 80, 200, 400, 700, float("inf")],
    labels=[
        "0-80 sec",
        "81-200 sec",
        "201-400 sec",
        "401-700 sec",
        "700+ sec",
    ],
)

print("\n=== DISTRACTION_TIMEOUT: recovery by inactivity ===")

print(
    distraction.groupby(
        "inactivity_bucket",
        observed=False
    )["was_recovered"]
    .agg(["mean", "count"])
    .rename(columns={
        "mean": "actual_recovery_rate",
        "count": "rows",
    })
)
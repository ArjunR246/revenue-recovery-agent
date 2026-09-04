import sqlite3

import pandas as pd
import numpy as np

from scipy.optimize import curve_fit


# ------------------------------------
# LOAD DATA
# ------------------------------------

conn = sqlite3.connect(
    "data/revenue_recovery.db"
)

df = pd.read_sql(
    """
    SELECT
        dropoff_cause,
        minutes_since_dropoff,
        was_recovered
    FROM checkouts
    """,
    conn
)

conn.close()

print("Rows loaded:", len(df))


# ------------------------------------
# BUCKETS
# ------------------------------------

bins = [
    0,
    15,
    30,
    60,
    120,
    180,
    360,
    720,
    1440,
    2880,
    100000
]

labels = [
    "0-15",
    "16-30",
    "31-60",
    "61-120",
    "121-180",
    "181-360",
    "361-720",
    "721-1440",
    "1441-2880",
    "2880+"
]

bucket_midpoints = {
    "0-15": 7.5,
    "16-30": 23,
    "31-60": 45,
    "61-120": 90,
    "121-180": 150,
    "181-360": 270,
    "361-720": 540,
    "721-1440": 1080,
    "1441-2880": 2160,
    "2880+": 4320
}

df["time_bucket"] = pd.cut(
    df["minutes_since_dropoff"],
    bins=bins,
    labels=labels,
    include_lowest=True
)


# ------------------------------------
# DECAY FUNCTION
# ------------------------------------

def exponential_decay(
    t,
    A,
    k,
    C
):
    return (
        A * np.exp(-k * t)
        + C
    )


# ------------------------------------
# FIT FUNCTION
# ------------------------------------

def fit_for_cause(cause_df):

    grouped = (
        cause_df
        .groupby("time_bucket", observed=True)
        .agg(
            recovery_rate=(
                "was_recovered",
                "mean"
            ),
            rows=(
                "was_recovered",
                "size"
            )
        )
        .reset_index()
    )

    grouped["t"] = (
    grouped["time_bucket"]
    .astype(str)
    .map(bucket_midpoints)
    .astype(float)
)

    grouped = grouped[
        grouped["rows"] >= 30
    ]

    x = grouped["t"].values
    y = grouped["recovery_rate"].values
    w = grouped["rows"].values

    params, _ = curve_fit(
        exponential_decay,
        x,
        y,
        p0=[
            0.6,
            0.0005,
            0.15
        ],
        sigma=1 / np.sqrt(w),
        maxfev=10000
    )

    return grouped, params


# ------------------------------------
# OVERALL
# ------------------------------------

print("\n==============================")
print("OVERALL DECAY MODEL")
print("==============================")

overall_grouped, overall_params = fit_for_cause(df)

A, k, C = overall_params

print(
    f"A={A:.4f} "
    f"k={k:.6f} "
    f"C={C:.4f}"
)

half_life = np.log(2) / k

print(
    f"Half-life (minutes): "
    f"{half_life:.1f}"
)

print(
    f"Half-life (hours): "
    f"{half_life/60:.1f}"
)


# ------------------------------------
# PER ROOT CAUSE
# ------------------------------------

for cause in sorted(
    df["dropoff_cause"].unique()
):

    print(
        "\n=============================="
    )

    print(cause)

    print(
        "=============================="
    )

    grouped, params = fit_for_cause(
        df[
            df["dropoff_cause"]
            == cause
        ]
    )

    A, k, C = params

    half_life = np.log(2) / k

    print(
        f"A={A:.4f}"
    )

    print(
        f"k={k:.6f}"
    )

    print(
        f"C={C:.4f}"
    )

    print(
        f"Half-life: "
        f"{half_life:.1f} min "
        f"({half_life/60:.1f} hrs)"
    )

    print("\nObserved points")

    print(
        grouped[
            [
                "time_bucket",
                "recovery_rate",
                "rows"
            ]
        ]
    )
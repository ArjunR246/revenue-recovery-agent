import sqlite3
import pandas as pd
import numpy as np

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

# =====================================================
# LOAD DATA
# =====================================================

conn = sqlite3.connect(
    "data/revenue_recovery.db"
)

df = pd.read_sql(
    """
    SELECT *
    FROM checkouts
    """,
    conn
)

conn.close()

print(f"Rows loaded: {len(df)}")

# =====================================================
# BUCKETS
# =====================================================

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

df["time_bucket"] = pd.cut(
    df["minutes_since_dropoff"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

bucket_midpoints = {
    "0-15": 7.5,
    "16-30": 22.5,
    "31-60": 45,
    "61-120": 90,
    "121-180": 150,
    "181-360": 270,
    "361-720": 540,
    "721-1440": 1080,
    "1441-2880": 2160,
    "2880+": 4320
}

# =====================================================
# DECAY FUNCTION
# =====================================================

def exponential_decay(t, A, k, C):
    return A * np.exp(-k * t) + C

# =====================================================
# ANALYZE ONE CAUSE
# =====================================================

def analyze_cause(df_subset, cause_name):

    grouped = (
        df_subset.groupby("time_bucket")
        .agg(
            recovery_rate=("was_recovered", "mean"),
            rows=("was_recovered", "count")
        )
        .reset_index()
    )

    grouped["minutes"] = grouped[
        "time_bucket"
    ].map(bucket_midpoints)

    print("\n")
    print("=" * 60)
    print(cause_name)
    print("=" * 60)

    # -------------------------------------------------
    # EARLY BUCKETS
    # -------------------------------------------------

    early = grouped[
        grouped["time_bucket"].isin(
            ["0-15", "16-30", "31-60"]
        )
    ]

    print("\nEarly Buckets")
    print(early[
        [
            "time_bucket",
            "recovery_rate",
            "rows"
        ]
    ])

    # -------------------------------------------------
    # FIT CURVE
    # -------------------------------------------------

    fit_df = grouped[
        grouped["rows"] >= 25
    ].copy()

    x = fit_df["minutes"].astype(float).values
    y = fit_df["recovery_rate"].values

    params, _ = curve_fit(
        exponential_decay,
        x,
        y,
        p0=[0.3, 0.001, 0.2],
        maxfev=10000
    )

    A, k, C = params

    predicted = exponential_decay(
        x,
        A,
        k,
        C
    )

    r2 = r2_score(
        y,
        predicted
    )

    print("\nFit Quality")
    print(f"R² = {r2:.4f}")

    # -------------------------------------------------
    # INTERVENTION WINDOW
    # -------------------------------------------------

    half_life_minutes = np.log(2) / k

    recommended_window = (
        half_life_minutes * 0.5
    )

    print("\nDecay Parameters")
    print(f"A={A:.4f}")
    print(f"k={k:.6f}")
    print(f"C={C:.4f}")

    print(
        f"Half-life: "
        f"{half_life_minutes:.1f} min "
        f"({half_life_minutes/60:.1f} hrs)"
    )

    print(
        f"Recommended intervention window: "
        f"{recommended_window:.0f} min "
        f"({recommended_window/60:.1f} hrs)"
    )

    return {
        "cause": cause_name,
        "r2": r2,
        "half_life_minutes": half_life_minutes,
        "recommended_window_minutes":
            recommended_window
    }

# =====================================================
# RUN
# =====================================================

results = []

for cause in sorted(
    df["dropoff_cause"].unique()
):

    subset = df[
        df["dropoff_cause"] == cause
    ]

    results.append(
        analyze_cause(
            subset,
            cause
        )
    )

print("\n")
print("=" * 60)
print("INTERVENTION WINDOW SUMMARY")
print("=" * 60)

summary = pd.DataFrame(results)

print(
    summary[
        [
            "cause",
            "r2",
            "half_life_minutes",
            "recommended_window_minutes"
        ]
    ]
)
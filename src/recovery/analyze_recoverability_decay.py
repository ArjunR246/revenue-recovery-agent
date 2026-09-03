import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

DB_PATH = "data/revenue_recovery.db"

TIME_BINS = [
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
    float("inf"),
]

TIME_LABELS = [
    "0-15 min",
    "16-30 min",
    "31-60 min",
    "61-120 min",
    "121-180 min",
    "181-360 min",
    "361-720 min",
    "721-1440 min",
    "1441-2880 min",
    "2880+ min",
]


# ============================================================
# Load data
# ============================================================

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql(
    """
    SELECT
        dropoff_cause,
        minutes_since_dropoff,
        was_recovered
    FROM checkouts
    """,
    conn,
)

conn.close()

print(f"Rows loaded: {len(df)}")


# ============================================================
# Create time buckets
# ============================================================

df["time_bucket"] = pd.cut(
    df["minutes_since_dropoff"],
    bins=TIME_BINS,
    labels=TIME_LABELS,
    include_lowest=True,
)


# ============================================================
# Overall recovery by time
# ============================================================

overall = (
    df.groupby(
        "time_bucket",
        observed=False
    )["was_recovered"]
    .agg(
        actual_recovery_rate="mean",
        rows="count",
    )
    .reset_index()
)

overall["recovery_rate_pct"] = (
    overall["actual_recovery_rate"] * 100
)

print("\n=== OVERALL RECOVERY BY TIME ===")
print(
    overall[
        [
            "time_bucket",
            "actual_recovery_rate",
            "recovery_rate_pct",
            "rows",
        ]
    ].to_string(index=False)
)


# ============================================================
# Root-cause recovery by time
# ============================================================

by_cause = (
    df.groupby(
        ["dropoff_cause", "time_bucket"],
        observed=False
    )["was_recovered"]
    .agg(
        actual_recovery_rate="mean",
        rows="count",
    )
    .reset_index()
)

by_cause["recovery_rate_pct"] = (
    by_cause["actual_recovery_rate"] * 100
)

print("\n=== RECOVERY BY TIME AND ROOT CAUSE ===")

for cause in sorted(df["dropoff_cause"].unique()):

    print(f"\n--- {cause} ---")

    cause_data = by_cause[
        by_cause["dropoff_cause"] == cause
    ]

    print(
        cause_data[
            [
                "time_bucket",
                "actual_recovery_rate",
                "recovery_rate_pct",
                "rows",
            ]
        ].to_string(index=False)
    )


# ============================================================
# Identify meaningful decay
# ============================================================

print("\n=== MEANINGFUL DECAY ANALYSIS ===")

DECAY_THRESHOLD = 0.15


def find_decay_point(data, group_name):

    data = data.copy()

    # Remove buckets with no observations.
    data = data[data["rows"] > 0].reset_index(drop=True)

    if len(data) == 0:
        return

    baseline = data.loc[
        0,
        "actual_recovery_rate"
    ]

    threshold_rate = baseline - DECAY_THRESHOLD

    decay_rows = data[
        data["actual_recovery_rate"] <= threshold_rate
    ]

    print(f"\n{group_name}")

    print(
        f"Early recovery rate: "
        f"{baseline:.3f}"
    )

    print(
        f"Meaningful-decay threshold: "
        f"{threshold_rate:.3f}"
    )

    if len(decay_rows) > 0:

        first_decay = decay_rows.iloc[0]

        print(
            "First bucket at or below "
            "15 percentage points below baseline:"
        )

        print(
            f"  {first_decay['time_bucket']}"
        )

        print(
            f"  Recovery rate: "
            f"{first_decay['actual_recovery_rate']:.3f}"
        )

        print(
            f"  Rows: "
            f"{int(first_decay['rows'])}"
        )

    else:

        print(
            "No bucket reached a 15 percentage-point "
            "decline from baseline."
        )


find_decay_point(
    overall,
    "OVERALL"
)

for cause in sorted(
    df["dropoff_cause"].unique()
):

    find_decay_point(
        by_cause[
            by_cause["dropoff_cause"] == cause
        ],
        cause,
    )


# ============================================================
# Candidate intervention windows
# ============================================================

print("\n=== CANDIDATE INTERVENTION WINDOWS ===")

for cause in sorted(
    df["dropoff_cause"].unique()
):

    cause_data = by_cause[
        by_cause["dropoff_cause"] == cause
    ].copy()

    cause_data = cause_data[
        cause_data["rows"] >= 20
    ].reset_index(drop=True)

    if len(cause_data) == 0:
        continue

    best_bucket = cause_data.loc[
        cause_data["actual_recovery_rate"].idxmax()
    ]

    print(f"\n{cause}")

    print(
        f"Highest observed recovery bucket: "
        f"{best_bucket['time_bucket']}"
    )

    print(
        f"Recovery rate: "
        f"{best_bucket['actual_recovery_rate']:.3f}"
    )

    print(
        f"Rows: "
        f"{int(best_bucket['rows'])}"
    )


# ============================================================
# Plot overall decay
# ============================================================

overall_plot = overall[
    overall["rows"] > 0
].copy()

x = np.arange(len(overall_plot))

plt.figure(figsize=(10, 6))

plt.plot(
    x,
    overall_plot["actual_recovery_rate"],
    marker="o",
)

plt.xticks(
    x,
    overall_plot["time_bucket"],
    rotation=45,
    ha="right",
)

plt.xlabel(
    "Minutes Since Dropoff"
)

plt.ylabel(
    "Observed Recovery Rate"
)

plt.title(
    "Overall Recoverability vs Time Since Dropoff"
)

plt.tight_layout()

plt.savefig(
    "data/recovery_decay_overall.png",
    dpi=150,
)

plt.show()


# ============================================================
# Plot root-cause decay curves
# ============================================================

plt.figure(figsize=(10, 6))

for cause in sorted(
    df["dropoff_cause"].unique()
):

    cause_plot = by_cause[
        by_cause["dropoff_cause"] == cause
    ]

    cause_plot = cause_plot[
        cause_plot["rows"] > 0
    ]

    x = np.arange(len(cause_plot))

    plt.plot(
        x,
        cause_plot["actual_recovery_rate"],
        marker="o",
        label=cause,
    )

plt.xticks(
    np.arange(len(TIME_LABELS)),
    TIME_LABELS,
    rotation=45,
    ha="right",
)

plt.xlabel(
    "Minutes Since Dropoff"
)

plt.ylabel(
    "Observed Recovery Rate"
)

plt.title(
    "Recoverability Decay by Root Cause"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "data/recovery_decay_by_cause.png",
    dpi=150,
)

plt.show()


print("\nSaved plots:")
print("  data/recovery_decay_overall.png")
print("  data/recovery_decay_by_cause.png")
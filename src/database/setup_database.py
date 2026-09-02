import sqlite3
from pathlib import Path

# Create database folder if needed
Path("data").mkdir(exist_ok=True)

conn = sqlite3.connect("data/revenue_recovery.db")

cursor = conn.cursor()

# --------------------------
# CHECKOUTS
# --------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS checkouts (
    checkout_id TEXT PRIMARY KEY,
    timestamp TEXT,

    amount REAL,
    payment_method TEXT,
    device_type TEXT,

    session_duration_seconds INTEGER,
    inactivity_seconds INTEGER,

    retry_count INTEGER,
    checkout_step_reached TEXT,

    network_quality TEXT,

    payment_status TEXT,
    failure_reason_code TEXT,

    otp_attempts INTEGER,
    upi_collect_expired INTEGER,

    dropoff_cause TEXT,

    recovered INTEGER,
    time_to_recovery_minutes INTEGER
)
""")

# --------------------------
# EVENTS
# --------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,

    checkout_id TEXT,

    event_timestamp TEXT,

    event_type TEXT,

    event_details TEXT
)
""")

# --------------------------
# PREDICTIONS
# --------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,

    checkout_id TEXT,

    predicted_cause TEXT,

    cause_confidence REAL,

    recoverability_score REAL,

    prediction_timestamp TEXT
)
""")

# --------------------------
# INTERVENTIONS
# --------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS interventions (
    intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,

    checkout_id TEXT,

    action_type TEXT,

    scheduled_time TEXT,

    executed_time TEXT,

    status TEXT
)
""")

# --------------------------
# RECOVERY RESULTS
# --------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS recovery_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,

    checkout_id TEXT,

    recovered INTEGER,

    recovered_amount REAL,

    recovery_time_minutes INTEGER
)
""")

# --------------------------
# AUDIT LOGS
# --------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,

    checkout_id TEXT,

    log_timestamp TEXT,

    module_name TEXT,

    decision TEXT,

    reasoning TEXT
)
""")

conn.commit()

print("Database created successfully")

conn.close()
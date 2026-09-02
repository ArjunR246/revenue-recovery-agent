# Revenue Recovery Agent – Progress Log

## Stage 1: Synthetic Data Generation

### Module

`src/data_generation/synthetic_generator.py`

### Purpose

Generates synthetic checkout sessions that simulate customer payment journeys and drop-offs.

### Input

None.

### Output

`data/raw/synthetic_checkouts.csv`

### Key Features

* Generates checkout IDs
* Simulates transaction amounts
* Simulates payment methods
* Simulates device types
* Simulates inactivity and retry behavior
* Assigns root causes of checkout abandonment
* Generates recovery outcomes

### How To Run

```bash
python src/data_generation/synthetic_generator.py
```

### Verification

```bash
python src/data_generation/inspect_patterns.py
```

### What I Learned

* How synthetic datasets are created
* How Pandas DataFrames work
* How CSV files are generated programmatically
* How feature engineering influences ML performance
* Why distinguishable patterns are important for classification models

---

## Stage 2: Pattern Inspection

### Module

`src/data_generation/inspect_patterns.py`

### Purpose

Validates that each root cause has distinct behavioral patterns.

### Output

* Average metrics by root cause
* Recovery rates by root cause
* Record counts by root cause

### How To Run

```bash
python src/data_generation/inspect_patterns.py
```

### What I Learned

* How group-by analysis works
* How to validate synthetic data quality
* How to identify useful predictive signals before model training

---

## Stage 3: Database Setup

### Module

`src/database/setup_database.py`

### Purpose

Creates the application database and required tables.

### Status

In Progress

### What I Expect To Learn

* SQLite fundamentals
* Database schema design
* Data persistence

---

## Stage 4: Data Loading

### Module

`src/database/load_checkouts.py`

### Purpose

Loads synthetic checkout data into the database.

### Status

In Progress

### What I Expect To Learn

* ETL pipelines
* CSV-to-database ingestion
* Data validation

---

# Architecture Notes

Synthetic Data
→ Data Validation
→ Database Storage
→ Feature Engineering
→ Root Cause Classifier
→ Recovery Recommendation Engine
→ Dashboard / API Layer

---

# Buildathon Pitch Notes

Problem:
Merchants lose revenue when customers abandon checkout.

Solution:
An AI-powered Revenue Recovery Agent that identifies why a checkout failed, predicts recovery likelihood, and recommends personalized recovery actions.

Business Impact:

* Increased conversion rate
* Reduced payment abandonment
* Improved customer experience
* Higher recovered revenue

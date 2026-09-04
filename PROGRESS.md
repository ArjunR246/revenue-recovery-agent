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
## Stage 5: Classifier Validation & Leakage Audit

### Purpose

Validate that the root cause classifier generalizes well beyond a single train/test split and confirm that no data leakage or duplication issues exist in the synthetic dataset.

### Validation 1: Cross-Validation

Performed 5-fold cross-validation using the same feature set and XGBoost classifier.

#### Fold Accuracies

* Fold 1: 0.9745
* Fold 2: 0.9780
* Fold 3: 0.9725
* Fold 4: 0.9740
* Fold 5: 0.9685

#### Summary

* Mean Accuracy: 0.9735
* Standard Deviation: 0.0031

#### Interpretation

The model performance is highly stable across folds, with all folds remaining within approximately one percentage point of each other. This indicates that the classifier is learning consistent patterns rather than relying on a favorable train/test split.

### Validation 2: Train/Test Leakage Check

#### Dataset Split

* Training Rows: 8000
* Testing Rows: 2000

#### Overlap Analysis

* Rows Appearing In Both Train And Test: 0
* Leakage Percentage: 0.0000%

#### Interpretation

No records were shared between the training and testing sets. The reported accuracy is therefore not inflated by train/test leakage.

### Validation 3: Duplicate Record Audit

#### Dataset Statistics

* Total Rows: 10000
* Exact Duplicate Rows: 0
* Duplicate Percentage: 0.00%

#### Interpretation

The synthetic dataset contains no exact duplicate checkout records. Model performance is not being artificially boosted through repeated examples.

### Conclusion

Cross-Validation Stability: PASS

Train/Test Leakage Check: PASS

Duplicate Data Audit: PASS

Model Generalization: PASS

Stage 5 Blockers: NONE

### Decision

The root cause classifier has passed stability, leakage, and duplication validation checks and is approved for progression to Stage 4 implementation work.

---
## Stage 6: Recoverability Scoring & Recovery Decay Modeling

### Purpose

Build a recoverability scoring system that predicts the probability of successfully recovering an abandoned checkout and quantifies how recovery likelihood decreases over time.

### Module

`src/recovery/train_recoverability_scorer.py`

### Business Question

Not all abandoned checkouts should receive the same recovery strategy.

This stage estimates:

* Which abandoned checkouts are most likely to recover
* How recovery probability changes over time
* Which root causes require faster intervention
* Which root causes remain recoverable for longer periods

### Dataset

* Total Rows: 10,000

### Overall Recovery Decay

Estimated decay parameters:

* A = 0.2068
* k = 0.001107
* C = 0.2533

Half-Life:

* 626.0 minutes
* 10.4 hours

### Root Cause Recovery Decay

#### DISTRACTION_TIMEOUT

Parameters:

* A = 0.2324
* k = 0.001017
* C = 0.2100

Half-Life:

* 681.7 minutes
* 11.4 hours

Interpretation:

Users who became distracted remain recoverable for a moderate period of time. Recovery effectiveness gradually declines over the first 12 hours.

#### OTP_FRICTION

Parameters:

* A = 0.2424
* k = 0.001232
* C = 0.3635

Half-Life:

* 562.7 minutes
* 9.4 hours

Interpretation:

OTP-related failures have the highest recovery potential but decay relatively quickly. Fast intervention is critical.

#### PAYMENT_FAILURE

Parameters:

* A = 0.1862
* k = 0.001026
* C = 0.2977

Half-Life:

* 675.8 minutes
* 11.3 hours

Interpretation:

Payment failures remain recoverable for a longer period than OTP failures and respond well to alternative payment recovery strategies.

#### PRICE_HESITATION

Parameters:

* A = 0.1292
* k = 0.000375
* C = 0.1080

Half-Life:

* 1846.8 minutes
* 30.8 hours

Interpretation:

Price-sensitive users have the lowest recovery rate but decay slowly. Promotional offers and delayed follow-ups may still be effective.

### Key Findings

1. Recovery probability is strongly time-dependent.
2. OTP_FRICTION has the highest recovery potential.
3. PRICE_HESITATION has the lowest recovery probability.
4. Different root causes require different recovery timing strategies.
5. Recovery intervention timing should be personalized based on predicted root cause.

### Business Impact

The Revenue Recovery Agent can prioritize outreach based on both:

* Root cause
* Predicted recoverability

This enables merchants to allocate recovery efforts where the expected revenue return is highest.

### Status

PASS

### Stage 6 Blockers

NONE

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

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

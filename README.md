# 💰 AI Revenue Recovery Agent
### Razorpay Buildathon Submission — Track 03: AI Revenue Recovery

An AI agent that looks at an abandoned checkout, figures out *why* it was
abandoned, estimates *how likely* it still is to be recovered, models how
that likelihood fades over time, and then decides whether it's even worth
intervening — and if so, how. Every decision comes with a reason attached,
and the agent knows when to stop trying.

---

## Why this exists

Most "cart recovery" systems do the same thing for every abandoned
checkout: wait some fixed amount of time, send a generic reminder, maybe
repeat it a couple more times. That treats a customer who hit an OTP
timeout the same as one who's still on the fence about the price — which
doesn't really make sense once you think about it. Someone who got
kicked out by a technical glitch is a very different problem than someone
who's just hesitating.

So instead of one blanket strategy, this project asks, per checkout:

1. What actually went wrong here?
2. Given that, how recoverable is this customer right now?
3. How fast does that window close?
4. Is it even worth spending effort on this one, and if so, what's the
   best action?

That last question is the one most systems skip, and it's the one this
project is built around.

---

## How it's put together

Synthetic checkout data (10,000 records)
->
Root cause classifier (XGBoost)
->
Recoverability scorer (XGBoost, probability output)
->
Recoverability decay model (fitted curve, per root cause)
->
Decision engine (Expected Recovery Value routing)
->
Stopping rules (max touches / cooldown / hard expiry / negative signals)
->
Recovery executor (simulated payloads)
->
Audit trail
->
Dashboard + baseline comparison


---

## The part I'd actually call the differentiator: decay curves

Almost every recovery system implicitly assumes recoverability is flat —
a customer is either "gettable" or not, regardless of how long ago they
dropped off. That felt wrong to me, so I modeled recoverability as
something that decays over time, and fit a separate curve per root cause:

recoverability(t) = A · e^(−k·t) + C


| Root Cause | A | k | C | Half-life |

| OTP_FRICTION | 0.2424 | 0.001232 | 0.3635 | ~9.4 hrs |

| PAYMENT_FAILURE | 0.1862 | 0.001026 | 0.2977 | ~11.3 hrs |

| DISTRACTION_TIMEOUT | 0.2324 | 0.001017 | 0.2100 | ~11.4 hrs |

| PRICE_HESITATION | 0.1292 | 0.000375 | 0.1080 | ~30.8 hrs |

The thing that actually validated this approach for me: PRICE_HESITATION
decays almost 3x slower than the other causes. That matches how I'd
expect real people to behave — someone still deciding whether to spend
the money doesn't just vanish after a couple hours the way someone who
hit a dead-end technical error does. This one number is what the whole
timing strategy is built around.

---

## How the agent decides what to do

Every possible action gets scored with an Expected Recovery Value(ERV):
ERV(action, t) = recoverability(t) × amount × action_cost_multiplier


The agent takes whichever valid action has the highest ERV for that
root cause (e.g. a payment-method suggestion only makes sense if the
cause was actually a payment failure; a discount only kicks in above a
minimum order value, since it's not worth giving away margin on a ₹200
cart). Cheap actions like a nudge stay viable across a wide range of
situations — expensive ones like a discount or a human escalation only
win when the amount and recoverability actually justify the cost.

### Stopping rules

Because an agent that never stops contacting people isn't compliant,
isn't nice, and isn't realistic:

- Max 3 touches per checkout
- 6-hour minimum cooldown between touches
- Hard stop at 72 hours no matter what
- Immediate stop on opt-out, repeated ignored interventions, or
  recoverability dropping below a floor

---

## Results

Ran across a batch of 10,000 simulated checkouts:

| Metric | Value |
|---|---|
| At-risk revenue | ₹61,137,168 |
| Recovered revenue | ₹9,382,482 |
| Overall recovery rate | 15.35% |
| Recovery rate among contacted checkouts | 39.51% |
| Checkouts actually contacted | 42.9% |

### Against a naive baseline

The baseline here is deliberately dumb: nudge every single abandoned
checkout, no diagnosis, no timing, no stopping rules.

| Metric | AI Agent | Baseline |
|---|---|---|
| Checkouts contacted | 42.9% | 100% |
| Recovered revenue | ₹9,382,482 | ₹21,765,369 |
| **Revenue per contact** | **₹2,187** | **₹2,177** |
| Touches per recovery | 2.53 | 2.65 |

I want to be upfront about what this table actually shows, because the
raw revenue numbers alone make the baseline look better, and that's not
the full story. **Revenue per contact is basically identical between the
two** — meaning the agent is finding almost the same value per customer
it reaches as the "contact everyone" approach. The difference is that it
gets there while messaging 57% fewer people. The baseline's bigger total
number is just a function of brute-forcing every single checkout, not
evidence that blanket-nudging is the smarter strategy — it's spending a
lot more contact volume, cost, and customer annoyance to land in
roughly the same place per touch.

---

## Things I'm not going to pretend are perfect

- **The classifier's confidence sits around 99.9% almost every time.**
  That's not a display bug — it's real output — but it's because my
  synthetic root-cause signals, even after I deliberately added overlap
  and label noise, are still cleaner than real customer behavior would
  be. Real data would almost certainly produce more varied, more modest
  confidence scores.
- **The recoverability scorer's AUC and Brier score are decent, not
  amazing**, after I intentionally toned down the noise I'd originally
  added to avoid an earlier overfitting problem (more on that below). I
  chose a believable, non-leaking model over one that looked
  artificially perfect.
- **Everything here is synthetic data.** The decay curves and recovery
  outcomes are simulated from distributions I designed, not pulled from
  actual Razorpay transactions. The pipeline is built so it could be
  recalibrated against real data without changing the architecture.
- **The executor is simulated, not live.** It builds correctly
  structured Razorpay-style payloads (payment links, discount coupons,
  escalation tickets) and logs what it would send, rather than actually
  calling test-mode APIs — a live integration was more than I could
  responsibly finish in the time I had.

## Mistakes I caught along the way (and fixed)

I think this is actually worth including, because catching these felt
like the real work:

- My root cause classifier first came back at **100% accuracy**, which
  is a red flag, not a win. Turned out my synthetic data was too clean
  — I went back and added overlapping feature ranges, some cross-class
  signal bleed, and 3% deliberate label noise, then retrained down to a
  more believable **97.35%** (checked with 5-fold cross-validation —
  mean 97.35%, std only 0.31% — and confirmed there was no train/test
  leakage or duplicate rows).
- My first version of the recoverability scorer barely beat a naive
  "just guess the root cause's average recovery rate" baseline. The
  noise I'd added to the generator was drowning out the actual
  behavioral signal (retry count, inactivity, OTP attempts), so I
  dialed it back until those features actually mattered, and verified
  the improvement before moving on.
- The decay-curve-derived intervention windows initially came out to
  as long as 5.5 days for PRICE_HESITATION — which directly contradicts
  the 72-hour hard-expiry rule I'd already committed to elsewhere in the
  system. I capped every decay-derived window at 4,320 minutes so the
  Decision Engine and Stopping Rules module actually agree with each
  other.

---

## Stack

- **Backend / ML**: Python, pandas, XGBoost, scikit-learn
- **Storage**: SQLite
- **Dashboard**: Streamlit, Plotly
- **Simulated integration**: Razorpay-style payload structures (Payment
  Links, discount coupons)

## Repo layout
src/
    data_generation/ synthetic checkout data generator
    database/ SQLite schema + loading
    diagnosis/ root cause classifier + validation
    recovery/ recoverability scoring + decay curve fitting
    routing/ decision engine (ERV) + stopping rules
    execution/ simulated executor + audit logging
    evaluation/ baseline comparison
    data/ generated datasets, model outputs, audit logs
    dashboard.py Streamlit dashboard


## Running it

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# full pipeline (outputs already included in data/ if you just want to explore)
python src/data_generation/synthetic_generator.py
python src/database/setup_database.py
python src/database/load_checkouts.py
python src/diagnosis/train_root_cause_classifier.py
python src/recovery/train_recoverability_scorer.py
python src/recovery/fit_decay_model.py
python src/routing/stopping_rules.py
python src/routing/decision_engine.py
python src/execution/recovery_executor.py
python src/evaluation/baseline_comparison.py

streamlit run dashboard.py
```

---

## What I'd do next with more time

- Calibrate the decay curves against real drop-off/recovery logs instead
  of simulated ones
- Wire the executor to actual Razorpay test-mode webhooks and the
  Payment Links API
- Add SHAP explainability on top of the classifier for richer audit
  reasoning
- Swap the point-estimate decay curves for proper survival analysis
  (Kaplan-Meier) once there's real censored recovery-time data to work
  with

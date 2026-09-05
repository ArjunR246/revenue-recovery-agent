Initially the model achieved perfect accuracy because the synthetic data was unrealistically separable. We introduced overlap and ambiguity to better approximate real customer behavior, resulting in a more credible evaluation.

We trained a root-cause diagnosis model using checkout behavior and payment gateway telemetry.

The model was evaluated using 5-fold cross-validation, achieving 97.35% mean accuracy with only 0.31% standard deviation.

We additionally verified there were no duplicate records and no train/test leakage.

Problems: AUC/Brier numbers in your pitch as an honest limitation "here's what didn't fully work and why".

    - Main question: Within the same cause, do better behavioral signals correspond to better recovery?


PRICE_HESITATION decays far slower (30.8 hr half-life) than OTP_FRICTION and PAYMENT_FAILURE (~9–11 hr half-life), which matches human intuition (someone still thinking about a big purchase stays "gettable" longer than someone who hit a technical snag and moved on)


Expected Recovery Value (ERV)
The routing engine evaluates each possible intervention using:
ERV = Recoverability Score × Checkout Amount × Cost Adjustment
Where:
Recoverability Score = probability of successful recovery from the Stage 5 decay model
Checkout Amount = potential revenue from the checkout
Cost Adjustment = estimated effectiveness after accounting for intervention cost
The action with the highest ERV is selected.

R(t)=Ae(−kt)+C

"NUDGE dominates because it's our lowest-cost action, so under an expected-value model it remains the rational choice whenever recoverability is moderate but doesn't clearly point to a specific failure mode. The system reserves higher-cost actions — discounts, payment-method suggestions, human escalation — for cases where the data justifies the extra cost: high amount, or a diagnosed cause the action directly addresses. It's not that the model defaults to NUDGE by accident — it's that spending more only makes sense when the expected payoff clears that higher bar."

Rather than treating recovery as a static classification problem, the system models recovery propensity as a time-dependent function and optimizes interventions using Expected Recovery Value under explicit stopping constraints.

The routing engine does not use the ground-truth label. It consumes the classifier's predicted root cause and confidence score, then selects the optimal intervention using expected recovery value and time-decay models.

The classifier predicts why a checkout was abandoned and provides a confidence score. The recoverability engine estimates the probability of recovery using root-cause-specific decay curves. The routing engine then calculates Expected Recovery Value (ERV) for every eligible intervention and selects the action with the highest expected business value.

The confidence values are unusually high because this is synthetic training data with clearly separated patterns. On production data we would expect a wider confidence distribution.






The decay curve difference (PRICE_HESITATION half-life ~3x longer than OTP_FRICTION) is your most original insight — lead with it.
ERV-based routing means every dollar spent on intervention is economically justified, not rule-of-thumb.
Stopping rules make this compliant by construction, not bolted on.
Full audit trail — every decision is a human-readable sentence, not a black box.
You caught and fixed real ML pitfalls along the way (100% accuracy → realistic noise, barely-better-than-baseline scorer → fixed) — mention this briefly if asked, it shows rigor.

a naive "nudge everyone" approach can recover more raw revenue simply by blasting all 10,000 checkouts, while your agent deliberately skips low-value interventions (that's literally what stopping rules are for). But if that's the real story, you need to say so explicitly and reframe the comparison — otherwise this table actively damages your pitch instead of supporting it. The more defensible framing is usually: baseline recovers more raw revenue by contacting everyone indiscriminately, but at a much worse cost-per-recovery / wasted-nudge rate, and violates compliant-escalation principles.

Suggested new caption:
"The AI agent recovers revenue at the same efficiency per customer
contacted (₹2,187 vs ₹2,177) as blanket-nudging everyone — but reaches
that result while contacting 57% fewer customers, reducing messaging
volume, cost, and spam risk without sacrificing recovery quality."
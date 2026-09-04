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
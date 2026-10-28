# Worked example · Four batches, four decisions, one surprise

The monitor compares each incoming batch with the 896-row training reference. It computes PSI per feature, MAE against the batch's labels, slice errors, and a single decision. All numbers below are real output from `monitoring/run_monitor.py` on the course project.

## The batches

Each batch is 300 trips generated from the course generator with one property changed:

| Batch | Change | Purpose |
|---|---|---|
| `normal` | none (seed 101) | Establish that the monitor does not fire on ordinary variation |
| `zone_shift` | pickup zones concentrated in the centre | Drift without degradation |
| `rainy_peak` | 60% rain, traffic +0.18 | Moderate drift, small error increase |
| `storm` | 80% rain, traffic +0.30, distances +15% | Drift and a real performance breach |

The generator computes durations from the same physical rules, so the labels remain consistent with the inputs. In production, labels would arrive late and the performance section would be computed on the labelled subset — the drift section would look identical.

## `normal`

```text
=== normal ===
feature              psi  severity
distance_km        0.031  stable
passengers         0.005  stable
traffic_index      0.055  stable
driver_supply      0.027  stable
weather            0.000  stable
pickup_zone        0.027  stable
mae 2.553 vs baseline 2.769 (-7.8%)
decision: no_action
```

Every PSI is far below 0.10. The MAE is 7.8% *better* than the baseline because a 300-row sample has its own variation — a reminder that a single batch's metric is an estimate, not a verdict.

## `zone_shift`: the surprise

```text
=== zone_shift ===
distance_km        0.598  alert
passengers         0.007  stable
traffic_index      0.026  stable
driver_supply      0.055  stable
weather            0.004  stable
pickup_zone        0.622  alert
mae 1.821 vs baseline 2.769 (-34.2%)
  ALERT drift: distance_km psi 0.598 >= 0.25
  ALERT drift: pickup_zone psi 0.622 >= 0.25
decision: investigate_drift
```

This is the module's most important result. Two features are far outside the alert band, and the model's error **improved by 34%**.

Why: the batch contains more central-zone trips, which are shorter and less variable, and the model handles them well. The inputs changed; the relationship did not. The model was asked easier questions.

A pipeline that treated "PSI > 0.25" as "retrain" would have replaced a model performing at 1.82 MAE with one trained to be good at the old mix. The correct action is to investigate — is the *product* changing (a new service area, a marketing campaign), and does the new mix persist? — and to change nothing about the model yet.

Note that the distance PSI is high as a consequence of the zone shift, not an independent signal. Correlated features produce correlated alerts; reading them as two findings double-counts one change.

## `rainy_peak`: drift, a small cost

```text
=== rainy_peak ===
distance_km        0.031  stable
traffic_index      0.194  warn
driver_supply      0.070  stable
weather            1.379  alert
pickup_zone        0.027  stable
mae 2.955 vs baseline 2.769 (+6.7%)
  ALERT drift: weather psi 1.379 >= 0.25
decision: investigate_drift
```

Weather shifts from 13% rain to 60% rain. The weather PSI is enormous because the category proportions invert; the traffic PSI rises to 0.194 (warn) because rain increases congestion in the generator.

Error rises 6.7%, below the 15% performance threshold. The decision is a ticket, not a page: look at the weather forecast, check whether the rain is a one-week event, and watch the next batch. If rain persists for a month, the model should be retrained on rain-heavy data — but the trigger is persistence plus a sustained error, not the first wet week.

The categorical PSI of 1.379 also illustrates a limitation: PSI for a three-category variable is a blunt instrument. A large value means "the mix is very different", not "the model is broken".

## `storm`: drift and degradation

```text
=== storm ===
distance_km        0.169  warn
passengers         0.005  stable
traffic_index      0.311  alert
driver_supply      0.135  warn
weather            2.880  alert
pickup_zone        0.027  stable
mae 3.683 vs baseline 2.769 (+33.0%)
  ALERT drift: traffic_index psi 0.311 >= 0.25
  ALERT drift: weather psi 2.880 >= 0.25
  ALERT performance: mae 3.683 is 33.0% above baseline 2.769
decision: retrain_review
```

This batch has both signals: multiple features outside the band and a performance breach more than twice the 15% threshold. The decision changes from "investigate" to "retrain review" because the evidence now includes the target.

The slice table explains who is affected:

```json
"Z06": {"mae": 5.476, "rows": 22},
"Z07": {"mae": 10.384, "rows": 19},
"Z08": {"mae": 5.873, "rows": 21}
```

Z07's error is 10.4 minutes against a baseline of 5.17, on 19 rows. That is a signal to investigate, not proof: 19 rows is a small sample, and the storm is an unusual event. The right sequence is:

1. Confirm the labels and the row count.
2. Check that the feature pipeline produced correct traffic values (a unit bug would look the same).
3. Decide whether the storm is representative of a persistent change or a transient event.
4. If persistent, train a candidate on recent data including storm-like conditions, evaluate on a *later* window, and run the promotion gate.

## The prediction log behind the numbers

```text
$ wc -l monitoring/predictions.jsonl
1200
$ head -2 monitoring/predictions.jsonl
{"logged_at": "2026-10-24T03:27:52+00:00", "batch": "normal", "trip_id": "T000095", "prediction": 15.05, "model_version": "1"}
{"logged_at": "2026-10-24T03:27:52+00:00", "batch": "normal", "trip_id": "T000270", "prediction": 12.43, "model_version": "1"}
```

Four batches × 300 rows = 1,200 lines. The `trip_id` is the join key to the eventual `duration_min`; `model_version` makes it possible to separate predictions from before and after a promotion. `logged_at` is in UTC.

In production this log is the expensive part: volume, storage, retention, and privacy. The reference keeps it simple deliberately — a JSONL file the monitor can read — but the fields are the ones a real system needs.

## What the four batches establish

| Claim | Evidence |
|---|---|
| Drift can be severe while accuracy improves | `zone_shift`: PSI 0.598/0.622, MAE −34.2% |
| Drift without a performance breach should not page | `rainy_peak`: one alert, +6.7%, ticket |
| Two signals justify a different decision | `storm`: drift + 33% error → retrain review |
| A monitor needs a no-change baseline | `normal`: all PSI < 0.06, no alerts |
| Slices localise the harm | `storm` Z07 MAE 10.384 on 19 rows |
| A single batch's MAE is noisy | `normal` is 7.8% better than the reference |

## What the reference monitor does not do

- It has no label delay: performance is computed on the full batch. A production version computes drift immediately and performance when labels arrive, then reconciles.
- It does not test statistical significance. A KS test or a bootstrap interval would say whether a PSI difference is distinguishable from noise at 300 rows.
- It has no automatic retraining, by design: the output is a decision for a human, with the evidence attached.
- It monitors features that were logged; a feature missing from the log cannot be monitored, which is why the logging schema is a design decision and not an afterthought.

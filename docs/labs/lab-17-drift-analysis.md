# Lab 17 · Detect a distribution shift and decide whether to retrain

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L17 | Advanced | 4 hours | [14 · Monitoring and drift](../modules/14-monitoring-drift/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-17-drift-detection/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-17-drift-detection) — starter files, data generator, and acceptance checker.

## Scenario

Four weeks of traffic arrive. One week has a large shift in study hours with no
loss of accuracy. Another has no measurable shift in the inputs and a 94%
increase in error. A dashboard that alerts on either signal alone gets one of
those wrong.

You will compute a distribution-shape measure and a performance measure, then
turn the two into an action. The lesson is in the disagreement: **drift is not
proof of declining accuracy**, and stable inputs are not proof of a healthy
model.

## What you will be able to do

- Compute PSI over reference quantile bins and read it as a magnitude.
- Compare a model's error on a new batch with its error on the reference batch.
- Choose thresholds you can defend, and say what each one costs when wrong.
- Separate "investigate" from "retrain" using two signals.

## Prerequisites and setup

```bash
cd examples/labs/lab-17-drift-detection
python make_batches.py
python monitor.py --json artifacts/monitor.json
```

Expected: four batches of 220 rows, and a report that prints mean shifts and MAE
but leaves the decision unimplemented.

## Your task

Implement `psi()` and `decide()` in `monitor.py`. The checker compares the report
with the generated truth.

## Data and starter files

| File | Purpose |
|---|---|
| `make_batches.py` | Four weeks with known shifts |
| `monitor.py` | Starter: mean comparison and MAE, no PSI, no decision |
| `check_lab17.py` | Validates PSI, severity, performance and decision |

| Batch | Construction | Expected behaviour |
|---|---|---|
| `week0` | Reference | Stable, decision `ok` |
| `week1` | Study hours multiplied by 1.4, same relationship | Drift warning, accuracy holds |
| `week2` | Identical inputs, scores 7 points higher | No drift, accuracy falls |
| `week3` | Fresh sample from the reference distribution | Stable, decision `ok` |

## Steps

### 1. Watch the average miss the first case

Run the starter and read the mean comparison. Week 1's mean hours move from 1.86
to 2.60, and the MAE moves from 3.59 to 3.85 — a 7% increase, inside the
tolerance. The mean changed and the model still works.

### 2. Compute PSI

Use reference quantile bins (10 bins), replace zero proportions with `1e-6`, and
sum `(current% - reference%) * ln(current% / reference%)`. Do not bin on the
current batch; the reference defines the buckets.

Expected: `week1 hours = 0.2443` (warn), `prior_score = 0.0743`, `sleep_hours =
0.1123`.

### 3. Read the second case

Week 2 has PSI 0.0 on every feature — the inputs are the same rows with different
labels. MAE rises from 3.5938 to 6.9748, a relative change of +94.08%. No drift
measure could have found this; only the delayed label did.

### 4. Pick thresholds

The starter constants are 0.10 (warn), 0.25 (alert) and 15% relative MAE. Write
one sentence for each: what a false positive costs, what a false negative costs.
You will be asked to defend them.

### 5. Turn signals into an action

```python
no alerts                    -> ok
performance alert            -> retrain
feature alert without one    -> investigate
```

Performance first, because it is the signal that costs money. A feature alert
alone is a reason to look, not a reason to spend a training run.

### 6. Run the checker

```bash
python check_lab17.py
```

Expected: `19/19 checks passed`.

## Expected output

```text
week0: mae 3.594 (+0.0%), max psi 0.000 -> ok
week1: mae 3.847 (+7.0%), max psi 0.244 -> investigate
week2: mae 6.975 (+94.1%), max psi 0.000 -> retrain
week3: mae 3.654 (+1.7%), max psi 0.091 -> ok
alerts: ['week1: investigate', 'week2: retrain']
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | All four weeks reported | Four entries with per-feature PSI |
| 2 | Reference week stable | All severities `stable`, decision `ok` |
| 3 | Week 1 hours detected | Severity `warn` or `alert` |
| 4 | Week 1 accuracy holds | Relative change < 0.15 |
| 5 | Week 1 decision | `investigate` |
| 6 | Week 2 inputs unchanged | Max PSI < 0.10 |
| 7 | Week 2 accuracy falls | Relative change ≥ 0.15 |
| 8 | Week 2 decision | `retrain` |
| 9 | Week 3 quiet | Max PSI < 0.10, decision `ok` |
| 10 | Alerts list | Only week1 and week2 |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `nan` PSI everywhere | Binning the current batch | Quantiles from the reference only |
| PSI huge on the reference week | Comparing the batch with itself after resampling | Reference vs itself is 0; check your indices |
| Week 2 shows drift | You added the label to the feature list | PSI is computed on features, not on `score` |
| `decide` returns `retrain` for week1 | Performance compared before feature severity | Performance threshold is 15%, not 5% |
| Division by zero in PSI | Empty bin | Replace proportions of zero with `1e-6` |

## Reflection questions

1. Week 1's drift is 0.244, just under the alert threshold. What would change if
   the threshold were 0.20, and what would you need to know to choose?
2. Why can week 2's regression not be detected from inputs?
3. What is the cost of a false `retrain`, and who pays it?
4. Which of these two signals would you page on, and which would you put in a
   weekly report?

## Optional extension

Add a third signal: the share of requests whose prediction falls outside the
training range. Show whether it would have flagged week 1, week 2, both or
neither, and explain the result.

## Cleanup

```bash
rm -rf data artifacts
```

PowerShell: `Remove-Item data, artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I saw a week with drift and stable accuracy
- [ ] I saw a week with a regression and no drift
- [ ] PSI uses reference-defined bins
- [ ] The decision rule uses both signals
- [ ] `check_lab17.py` reports `ACCEPTED`

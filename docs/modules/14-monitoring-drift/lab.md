# Guided lab · Four batches, one false alarm, one real one

**Time:** 6 hours. **Tools:** Python 3.11/3.12, pandas, NumPy, scikit-learn, matplotlib optional. CPU only; no monitoring service or cloud account.

## Scenario and business problem

After a stormy week, support reports that ETA estimates felt wrong in the outer zones. Engineering looks at the dashboard: latency is fine, error rate is zero, the model is the one that was promoted last month. Nobody can answer the three questions that matter: *is the input different, is the model worse, and should we do anything?*

You will build the instrumentation that answers them, backtest it on four batches with known behaviour, and write the decision record. The hardest part is not computing PSI; it is refusing to retrain when the numbers look alarming but the model is fine.

### Skills practised

- Designing a prediction log that supports later label joins.
- Computing PSI against a stated reference and reading it honestly.
- Measuring performance when labels arrive late.
- Distinguishing drift from degradation.
- Setting thresholds with a stated cost, and separating a page from a ticket.
- Writing a decision and a runbook someone else can act on.

### Prerequisites

Modules 06, 09, 10, and 13. A served model, a registry, and a trained artifact. The generator from the course project, used with its shift options.

### Input data

- **Reference:** `data/features/train.csv` (896 rows).
- **Current batches:** four 300-row batches from the generator:
  - `normal` — no change;
  - `zone_shift` — central-zone weighting;
  - `rainy_peak` — 60% rain, traffic +0.18;
  - `storm` — 80% rain, traffic +0.30, distances ×1.15.

Labels are present because the data is synthetic. In production, treat them as arriving after a delay.

### Directory layout

```text
raviride-eta/
├── monitoring/
│   ├── drift.py
│   ├── run_monitor.py
│   ├── predictions.jsonl
│   └── reports/<batch>.json
└── docs/monitoring-runbook.md
```

## Part 1: log a prediction (45 minutes)

1. Add a prediction log line to the service (or to a batch script) with: timestamp (UTC), batch or request id, `trip_id`, prediction, model version.
2. Decide what *not* to log and write it down. At minimum: no passenger names, no phone numbers, no free-text addresses.
3. Record a sample line and the retention rule you would use if labels arrive after 14 days.
   **Checkpoint 1:** the log contains 300 lines for one batch, and every line has a key that can join to the eventual label.

*Recovery:* if the log has no join key, stop and add one. Performance monitoring is impossible without it, and no amount of drift analysis replaces it.

## Part 2: compute drift (60 minutes)

4. Implement `psi(reference, current, bins=10)` with quantile bins from the reference. Handle empty bins with a small epsilon.
5. Implement categorical PSI over value counts, with a minimum-count rule for categories.
6. Report per feature: PSI, severity band (stable < 0.10, warn < 0.25, alert ≥ 0.25), and the reference row count.
   **Checkpoint 2:** the `normal` batch produces all PSI values below 0.10. If not, your bins or reference are wrong.

## Part 3: compute performance (45 minutes)

7. Predict each batch and compute MAE, p95 absolute error, and per-zone MAE with row counts, against the labels.
8. Compare with the baseline `2.7686` and compute the relative change.
9. Write the label-coverage line: how many rows, how many labelled, and the assumed delay.
   **Checkpoint 3:** `storm` shows a double-digit percentage increase and `zone_shift` shows an improvement. If `zone_shift` looks worse, your batch generation or feature path differs.

## Part 4: the decision rule (45 minutes)

10. Implement a decision function:
    - no alert → `no_action`;
    - drift alerts only → `investigate_drift`;
    - performance beyond tolerance → `retrain_review`.
11. Print the alerts that drove the decision, with the values and thresholds.
    **Checkpoint 4:** four batches, four decisions, each traceable to specific lines in the report.

12. Write the thresholds table in your runbook: signal, threshold, page or ticket, and the cost of a false positive. Include the minimum sample size below which the monitor reports "insufficient data" instead of a value.

## Part 5: the false alarm (45 minutes)

13. Take `zone_shift`. Write a paragraph answering: what changed, why did accuracy improve, and what would you do this week?
14. Write the counterfactual: what would have happened if the pipeline retrained automatically on any PSI alert? Use the measured numbers.
    **Checkpoint 5:** your explanation names the mechanism (composition of trips, shorter central routes) rather than "the model is robust".

15. Check the correlated features: `distance_km` and `pickup_zone` both alert. Explain why they are one finding, not two.

## Part 6: the real alarm and the runbook (75 minutes)

16. For `storm`, follow the four questions from Concepts §9:
    - Is the metric real? (labels, row count)
    - Is the model at fault, or the pipeline?
    - Is the population representative or an event?
    - What would a candidate be evaluated on?
17. Decide: investigate, retrain, or roll back. Justify with two specific numbers and one slice.
18. Write `docs/monitoring-runbook.md`: the five first checks, the rollback command from Module 09, who approves a retrain, and the known blind spots (label delay, small slices, seasonality).
    **Checkpoint 6:** someone who has not done the lab can follow the runbook to reach the same decision.
19. Inject a known shift as a test of the monitor: regenerate `storm` with an even higher traffic delta and confirm the alert fires. Record it as a monitor test.

## Expected outputs

| Batch | Drift | MAE (baseline 2.7686) | Decision |
|---|---|---|---|
| `normal` | all PSI < 0.06 | 2.553 (−7.8%) | `no_action` |
| `zone_shift` | distance 0.598, zone 0.622 | 1.821 (−34.2%) | `investigate_drift` |
| `rainy_peak` | weather 1.379, traffic 0.194 | 2.955 (+6.7%) | `investigate_drift` |
| `storm` | weather 2.880, traffic 0.311 | 3.683 (+33.0%) | `retrain_review` |

Slice evidence for `storm`: Z07 MAE 10.384 on 19 rows, against a baseline of 5.17.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Logging | Join key, UTC timestamp, model version, retention rule, no unnecessary personal data |
| Reference | Window stated, row count recorded, choice justified |
| Drift | PSI computed from reference bins; severity bands; correlated features explained |
| Performance | Label coverage and delay stated; slice metrics with row counts |
| Thresholds | Each threshold has a page/ticket decision and a false-positive cost |
| Decision | Four decisions, each with cited values; no automatic retrain |
| Runbook | Followable by someone else; includes rollback and blind spots |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| All PSI values are zero | Comparing a batch with itself, or bins too wide | Check the reference frame; use quantile bins |
| PSI explodes on one category | A category with one or two rows | Minimum-count rule; merge rare categories |
| MAE is NaN | Labels missing or misaligned after a join | Check the join key and row counts |
| `storm` improves accuracy | Generator options not applied, or the model retrained on shifted data | Regenerate with the documented options |
| Alerts on every batch | Reference too old, or thresholds too tight | Re-baseline or loosen; record the decision |
| Performance looks perfect | Labels leaked into features | Check `feature_frame` for the target or `fare_amount` |

## Cleanup

- Keep `monitoring/reports/` as evidence; it is small.
- Delete the prediction log if it contains data you would not keep in production; otherwise keep it and state the retention rule.
- No services were started.

## Optional extensions

1. **Statistical significance.** Add a bootstrap confidence interval for MAE on each batch and state whether the `rainy_peak` increase is distinguishable from noise at 300 rows.
2. **KS instead of PSI.** Add a two-sample Kolmogorov–Smirnov statistic for numeric features and compare which batch it flags first. Explain the disagreement.
3. **Alert simulation.** Replay 30 days of batches (generate with varying seeds and one injected storm week) and report how many pages and tickets your thresholds would have produced. That number is the argument for or against the thresholds.

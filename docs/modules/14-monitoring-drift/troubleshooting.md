# Troubleshooting · Module 14

## Diagnose in this order

1. **Is the model the one you think?** `/model-info` or the prediction log's `model_version`.
2. **Is the input what you think?** Schema, null rate, unseen categories, units.
3. **Is the metric real?** Label coverage, row count, join key.
4. **Is it a slice problem?** The aggregate may be fine while one zone collapses.
5. **Is it the world or the pipeline?** Drift plus a pipeline defect looks like concept drift.

## Failure table

| Symptom | Likely cause | Fix |
|---|---|---|
| Every PSI is huge | Reference is stale, or units changed | Re-baseline; check schema and units first |
| Every PSI is zero | Comparing a batch with itself | Check that reference and current are different frames |
| PSI moves wildly day to day | Small batches, too many bins | Minimum sample size; fewer bins; smooth over a window |
| MAE is `NaN` | Labels missing or join failed | Check the join key and labelled row count |
| Performance looks perfect | Target or `fare_amount` leaked into features | Inspect `feature_frame` and the feature set |
| Drift alerts but no performance change | Covariate shift, or a feature the model barely uses | Investigate; do not retrain reflexively |
| Performance drops with no drift | Label shift, concept drift, or a pipeline bug | Check labels and recent deploys before the model |
| Alerts stop entirely | Monitor job failed silently | Monitor the monitor: heartbeat and last-success timestamp |
| Alert storms after a deploy | Traffic pattern changed with the release | Compare with the deploy timeline; consider a temporary reference |
| Slice metric unstable | Few rows in the slice | Report counts; raise the minimum; aggregate over weeks |

## Case 1: "PSI says drift, accuracy says fine"

This is the reference `zone_shift` case: distance PSI 0.598, zone PSI 0.622, MAE 1.821 against a baseline of 2.769. The model is doing better because the new mix is easier.

What to do:

1. Confirm the mix change is real and persistent (a week, not an hour).
2. Check the slices: does any population get worse even if the aggregate improves?
3. Update the evaluation set if the product has genuinely changed, and record why.
4. Do not retrain merely because PSI is high.

The failure mode to avoid is a monitor that treats drift as a proxy for accuracy. It is a proxy for *change*, and change can be good.

## Case 2: "accuracy dropped but nothing drifted"

Three candidates, in order:

- **Label shift or concept drift**: inputs look normal, the relationship moved. Needs labels to confirm; retrain on recent data if sustained.
- **Pipeline defect**: a feature computed differently, a stale artifact, a unit bug. Check model version, feature code commit, and a single-record comparison against the training path (Module 10).
- **Evaluation defect**: the labels are wrong, late, or joined incorrectly. Check a handful of rows by hand before believing the metric.

A drop with no drift is more alarming than a drop with drift, because the usual early-warning signal did not fire.

## Case 3: alerts nobody reads

Symptoms: dozens of alerts a week, most closed as "expected", the channel muted.

Fixes, in order:

1. **Raise the bar for a page**: require two independent signals.
2. **Add a minimum sample size** and an `insufficient_data` state.
3. **Route drift-only alerts to a ticket**, not a page.
4. **Review the last 30 alerts** and classify them; the false-positive pattern tells you which threshold is wrong.
5. **Delete alerts that never lead to action.** A dashboard can keep the number without waking anyone.

## Case 4: the monitor itself stops

A monitor that fails quietly is worse than no monitor. Symptoms: no alerts for weeks, a dashboard with a flat line, a last-updated timestamp that stopped moving.

Add:

- a heartbeat metric (the monitor ran at time T),
- a "last successful evaluation" timestamp on the dashboard,
- an alert when no evaluation has run for two expected intervals,
- a test that runs the monitor on a fixture with a known shift in CI (Module 12).

## Case 5: retraining made it worse

Common causes:

- the candidate was evaluated on the data that triggered the retrain;
- training data included the incident, but the test set did too, masking the regression on normal traffic;
- the label delay meant the newest labels were incomplete;
- the pipeline had a defect that the retrain reproduced.

Roll back to the previous version first (Module 09), then re-evaluate the candidate on a clean, later window before trying again.

## When to stop monitoring and fix the pipeline

If the input schema is wrong, no amount of drift analysis helps. Schema violations, null spikes, and unseen categories are pipeline defects; route them to the pipeline owner and fix them before interpreting any distribution metric. A monitor is a smoke detector, not a fire brigade.

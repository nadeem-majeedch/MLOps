# Lab 18 · Investigate a regression and decide whether to roll back

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L18 | Advanced | 3 hours | [14 · Monitoring and drift](../modules/14-monitoring-drift/index.md), [09 · Model registry](../modules/09-model-registry/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-18-regression-rollback/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-18-regression-rollback) — starter files, data generator, and acceptance checker.

## Scenario

A new version went live on 11 October. The overall error moved from 2.50 to
3.48, which reads as a bad week rather than an incident, and the daily average on
the dashboard does not jump. Somewhere in the traffic, a slice is much worse.

You have fourteen days of prediction logs with delayed labels, a version change
in the middle, and one hour to decide whether to roll back. The decision is not
"is the new model worse?" — it is "for whom, by how much, and what does that cost
against the cost of reverting?".

## What you will be able to do

- Locate a change point by slice, not by aggregate.
- Attribute an error increase to a version and a population.
- Compare the cost of a rollback with the cost of waiting for a retrain.
- Write a decision that another engineer can execute without you.

## Prerequisites and setup

```bash
cd examples/labs/lab-18-regression-rollback
python make_logs.py
python investigate.py
```

Expected: 1,960 predictions over 14 days, and a weekly table that shows the
regression without locating it.

## Your task

Extend `investigate.py` to compute per-day and per-slice error, identify the
change point and the worst slice, and write a decision. The checker recomputes
your numbers from the logs.

## Data and starter files

| File | Purpose |
|---|---|
| `make_logs.py` | 140 predictions/day, `v3` before 2026-10-11, `v4` after |
| `investigate.py` | Weekly aggregation only, with the report contract |
| `check_lab18.py` | Validates onset, slice numbers and the decision |

Log record: `request_id`, `when`, `version`, `hours`, `prior_score`,
`sleep_hours`, `prediction`, `actual`.

## Steps

### 1. Reproduce the aggregate

```bash
python investigate.py
```

The weekly view is enough to see that something changed and not enough to act.
That gap is the lab.

### 2. Compute daily error, then daily error by slice

Group by date and version; then restrict to `hours > 6` and group again. The
overall daily series stays flat because v4 improved short sessions by 0.16 while
degrading long ones by 4.9.

### 3. Find the change point

Compare each day's long-session MAE against the v3 median. The first sustained
jump is 2026-10-11, the release date — not 2026-10-04, which has a single
high-error observation with one long session.

### 4. Attribute the loss

| Slice | v3 MAE | v4 MAE | Delta |
|---|---|---|---|
| hours > 6 | 1.944 | 6.873 | +4.929 |
| hours <= 6 | 2.657 | 2.498 | -0.159 |
| prior_score < 50 | 2.484 | 4.250 | +1.766 |
| prior_score >= 50 | 2.506 | 3.307 | +0.801 |

The second-best slice is a consequence of the first: long sessions are more
common among lower prior scores. Name that in your report rather than treating
both as independent findings.

### 5. Decide

Rollback restores the previous behaviour in minutes and is reversible. Retraining
takes hours and depends on data you do not have yet: v4's training set apparently
dropped long sessions. The decision is rollback **and** a retrain task, not either.

Write the rationale with the numbers, the affected share of traffic, and the
version you are restoring.

### 6. Run the checker

```bash
python check_lab18.py
```

Expected: `15/15 checks passed`.

## Expected output

```text
onset 2026-10-11 on v4 (v3 long-session median mae 1.996)
overall: v3 2.5019 -> v4 3.4756 -- the average understates the change
  hours>6         v3 1.944  v4 6.873  delta +4.929
  hours<=6        v3 2.657  v4 2.498  delta -0.159
  prior_score<50  v3 2.484  v4 4.250  delta +1.766
  prior_score>=50 v3 2.506  v4 3.307  delta +0.801
decision: rollback to v3
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Change point | `2026-10-11` |
| 2 | Suspect version | `v4` |
| 3 | Worst slice | `hours>6` |
| 4 | Long-session MAE matches logs | Within 0.02 of recomputation |
| 5 | Regression is material | Delta > 3.0 |
| 6 | Daily detail complete | 14 dates |
| 7 | Slice-level daily series | At least 7 rows |
| 8 | Decision | `rollback` to `v3` |
| 9 | Rationale cites slice and a number | Present |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Onset detected on 2026-10-04 | Single sparse long-session day | Require a sustained jump or a minimum slice size |
| No onset found | Threshold too high | Compare with the v3 median, not the mean |
| Slice MAE differs from the checker | Grouping by all rows instead of `hours > 6` | Apply the mask before aggregating |
| `KeyError: 'correlation'` | pandas 2.2 removed `DataFrame.corrwith` default | Use `frame["a"].corr(frame["b"])` |
| Rollback cannot be executed | No previous version recorded | This is the Lab 09 lesson: rollback needs lineage |

## Reflection questions

1. The overall MAE rose 39% while one slice tripled. Which number would you put
   in the incident summary, and why?
2. Is `prior_score < 50` a separate finding or a symptom? How would you decide?
3. What would have detected this before release, and where would that check live?
4. Rollback restores v3, which also has a known weakness. What do you tell the
   business while the retrain happens?

## Optional extension

Quantify the decision: assume a 20-minute error costs 0.4 in rider satisfaction
units and a rollback costs one hour of engineer time. Compute the threshold at
which waiting for the retrain would have been cheaper, and state your assumptions.

## Cleanup

```bash
rm -rf data artifacts
```

PowerShell: `Remove-Item data, artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I saw that the weekly average hid the change
- [ ] I located the change point and attributed it to a version
- [ ] I found the slice where the error tripled
- [ ] My decision names the target version and the evidence
- [ ] `check_lab18.py` reports `ACCEPTED`

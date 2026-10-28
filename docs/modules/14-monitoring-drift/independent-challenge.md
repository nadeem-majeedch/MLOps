# Independent challenge · A monitor that survives a false alarm

## The brief

Design and implement a monitoring policy for the ETA service that would have caught the storm degradation without paging anyone during the zone-mix change. Then prove it on a month of simulated traffic.

The proof is a backtest: 30 daily batches with known behaviour, including one storm week, one zone-mix change, and ordinary variation. Report pages, tickets, and misses. A policy that pages every day is as useless as one that never fires.

## Requirements

1. **Two-signal rule.** At least one page condition must require two independent signals (drift plus performance, or performance plus a business proxy). State why the signals are independent.
2. **Minimum sample size.** Below it, the monitor reports `insufficient_data` instead of a value; no alert can fire on noise.
3. **Label delay.** Simulate labels arriving 48 hours after prediction. Drift is available immediately; performance is not. Show the alert timeline for one storm date: what fired at T+0, what fired at T+48h.
4. **Slices.** At least one population slice with its own threshold and row count.
5. **A decision record** per alert: investigate, retrain review, or false positive — with the evidence that justified it.
6. **A retraining trigger** that is a rule, not a feeling: for example, "performance breach on two consecutive labelled windows, with the slice breach persisting, and the candidate passes the Module 09 gates".

## Backtest design

Generate 30 daily batches of 300 rows:

| Days | Behaviour |
|---|---|
| 1–10 | Normal variation (different seeds) |
| 11–17 | Storm week (heavy rain, high traffic, longer distances) |
| 18–24 | Recovery to normal |
| 25–30 | Zone-mix change (central zones) |

Labels arrive at T+48h in your simulation. Compute, for each day: PSI per feature, MAE once labels are available, slices, and the decision.

## What to submit

- The backtest output: a table of 30 days with drift status, performance status, decision, and whether a human would have acted.
- Counts: pages, tickets, false positives, missed degradations.
- The alert timeline for one storm day, showing what was knowable before labels.
- The retraining rule, in one sentence plus the code that implements it.
- A one-page runbook.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Sensitivity | The storm week is flagged within two labelled days |
| Specificity | The zone-mix change does not page; ordinary variation does not alert |
| Noise control | No alert on a slice below the minimum sample size |
| Delay handling | The timeline distinguishes what was knowable at T+0 and T+48h |
| Decision | Every alert has a recorded outcome, including false positives |
| Rule | The retraining trigger is executable and cites evidence |

## Questions to answer

1. How many pages did your policy produce in 30 days, and how many were actionable?
2. Which single change most reduced false positives, and what did it cost in detection delay?
3. What would you monitor to catch a failure that produces no drift and no label change — for example, the wrong model version being served?
4. If labels stopped arriving entirely, what would your policy do? Should it page?

## Stretch

Add a **shadow evaluation**: score a candidate model on live traffic without serving it, and compare its MAE with the champion on the same labelled rows. Explain when shadow evaluation is better than retraining and when it is a waste of compute.

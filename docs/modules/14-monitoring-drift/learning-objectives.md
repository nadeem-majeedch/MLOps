# Learning objectives · Module 14

| # | Objective | Evidence |
|---|---|---|
| 1 | Log predictions usefully and lawfully | A schema, one sample line, retention, and a privacy note |
| 2 | Choose a reference window | A stated window with a reason and its row count |
| 3 | Compute and interpret drift | Per-feature PSI with severity bands and a caveat |
| 4 | Distinguish drift from degradation | A batch with high PSI and unchanged or better accuracy |
| 5 | Measure performance with late labels | A report that states label coverage and date |
| 6 | Set thresholds with a cost argument | A table of thresholds, expected alert volume, and false-positive cost |
| 7 | Decide investigate / retrain / roll back | A decision record citing metrics, not impressions |
| 8 | Write an actionable runbook | Steps someone else can follow without you |

## Monitoring-review criteria

A monitor is reviewable when an on-call engineer can answer these from the runbook and the dashboard:

- [ ] What is being measured, against which reference, over which window?
- [ ] Which signal triggers a page, and which only opens a ticket?
- [ ] What is the expected false-positive rate, and what does a false positive cost?
- [ ] What does "investigate" mean, concretely, in the first ten minutes?
- [ ] What evidence is required before retraining?
- [ ] Who can approve a retrain, and who can roll back?
- [ ] What happens to the alert when labels are delayed by a week?
- [ ] How is the monitor itself tested — has anyone injected a known shift?

## Drift is a symptom, not a diagnosis

Three findings can look identical on a dashboard and have different causes:

| Finding | Cause | Response |
|---|---|---|
| Input distribution changed | New routes, weather, a marketing campaign | Examine performance; often no retrain |
| Input–output relationship changed | Driver behaviour, road works, pricing change | Retrain with recent data |
| The service or pipeline broke | Wrong feature, stale model, unit bug | Fix the defect; a retrain makes it worse |

The module's reference batch with **high drift and better accuracy** is the proof that the first row exists in practice. A monitor that pages on PSI alone will, eventually, page for good news.

## Self-check before you start

You should have a served model (Module 10), a registry (Module 09), and a scheduled pipeline (Module 13). You do not need a monitoring platform; the reference implementation uses NumPy and pandas.

After the module, you can answer:

1. Why can PSI be high while accuracy improves?
2. What can you monitor before labels exist, and what must wait?
3. Why is a fixed threshold like 0.25 a starting point rather than a rule?
4. What is the difference between retraining and rolling back, and when is each correct?
5. What would make you distrust a drift alert entirely?

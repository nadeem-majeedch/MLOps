# Worked example · A reference lifecycle, and the incident that tests it

This example uses two artefacts that were actually run in the course environment:

- the advanced starter, [`examples/starters/advanced-monitoring-pipeline/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/starters/advanced-monitoring-pipeline), a complete small lifecycle on synthetic equipment data;
- the incident fixture, [`examples/labs/lab-20-incident/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-20-incident), a deterministic evidence pack for a failed release.

Neither is a submitted capstone. The starter is a template; the incident is a rehearsal. Together they show what the seven capstone artefacts look like when the evidence is real.

## The reference lifecycle

The starter predicts equipment failure within seven days. It is not RaviRide, but the lifecycle is the same, and the numbers are measured:

```text
$ python make_data.py
wrote data/equipment.csv      480 rows  37 positive
wrote data/current_batch.csv  160 rows  unlabelled, shifted

$ python -m pytest
29 passed

$ python cli.py train
train rows  360  machines ['M01', 'M02', 'M03', 'M04', 'M05', 'M06']
test        120 rows  held out ['M07', 'M08']
roc_auc     0.8382
pr_auc      0.4268
recall      0.8750 at threshold 0.0731 (chosen for 80% train recall)
precision   0.1707
confusion   tp=7 fn=1 fp=34
```

Three things in that output are worth more than the ROC AUC:

1. **The split is by machine, not by row.** Readings from one machine never appear on both sides. A random split would inflate the metric; the README asks you to measure the difference.
2. **The threshold was chosen before test.** It is the quantile of training positive scores that reaches 80% recall, frozen before the test set is touched. Choosing it on test would be leakage with extra steps.
3. **Precision is 0.17.** For every 7 true alarms there are 34 false ones. That is a deliberate trade with 8% prevalence and a missed failure costing more than an inspection. The capstone requires you to write the trade-off down, not to quote accuracy.

## Mapping to the seven artefacts

| Capstone artefact | What the starter shows | What it does not show |
|---|---|---|
| 1. Rerunnable pipeline from a clean clone | `make_data.py`, `cli.py`, pinned `requirements.txt`, README with exact commands | A timed clean-clone run by a peer |
| 2. Versioned data and model with provenance | Generated data, metrics, `run_meta.json`, registry version and champion alias | A remote registry, a data hash chain to a commit |
| 3. Automated tests and a CI gate that fails | 29 tests, `cli.py` exit codes, a workflow with the same commands | A hosted CI run; three injected regressions with retained output |
| 4. Served endpoint with validation | Not included | The API, contract, 422 cases |
| 5. Monitoring with an actionable alert | PSI report, drift verdict, exit code 2 | An alert with an owner and a first diagnostic step |
| 6. Runbook | README covers run, test, promote, rollback | A peer's timed deployment, top-three alert procedures |
| 7. Model card and defence | Limitations are in the README | A card with disparity and prohibited use; a defence |

The gaps are the capstone work. The starter gives you a shape, not a submission.

## The drift report, and what it does not say

```text
temperature_c          PSI  0.781  drift   mean 68.72 -> 74.32
vibration_mm_s         PSI  3.216  drift   mean 2.35 -> 3.2
pressure_bar           PSI  0.128  watch   mean 4.2 -> 4.18
operating_hours        PSI  0.058  stable  mean 4556.29 -> 4527.48
days_since_service     PSI  1.446  drift   mean 106.61 -> 143.76
verdict     drift
ALERT: input distribution moved. Find the cause before retraining.
```

The later batch has higher vibration, higher temperature, and more days since service. That is consistent with a maintenance interval being extended, which is an operational cause worth checking before blaming the model.

It does **not** say accuracy fell. The batch is unlabelled. To learn that, you need outcomes after seven days, a labelled holdout from the same period, and the same metric against the frozen threshold. Until then, "the inputs moved" is the whole claim. A capstone that retrains on this signal alone has confused drift with degradation.

## The incident: 128 minutes, 660 failed requests

The incident fixture is a different system and a different failure, but the evidence discipline is the capstone's.

At 02:00, release v5 replaced v4 outside the normal gate. It expected `traffic_index`, which the service did not send. Every prediction raised `KeyError` and returned 500. The first page fired at 02:12; the service was restored at 04:20.

The timeline, from the evidence pack:

```text
01:58:42  v5 starts and logs a schema warning
02:00:04  first 500
02:12:00  latency alert pages
02:18:00  5xx alert fires
02:22:51  acknowledgement, 11 minutes after the page
02:58:30  mismatch hypothesised
03:20:44  rollback blocked on approval
03:52:10  approval granted
04:20:00  alias moved to v4
04:24:00  alert resolved
```

The impact is computed, not estimated: 240 + 300 + 120 = **660 failed requests** in the 02:00–04:20 window. The MTTR is 128 minutes, from the first page (02:12) to the alias change (04:20). The 87 minutes between the rollback request and the approval are the largest single gap.

Root cause: the artefact required a feature the request schema did not provide, and nothing compared the two before traffic arrived. Contributing conditions:

1. the gate was overridden for the hotfix, so the contract test never ran;
2. the rollout went to 100% with no canary;
3. rollback required an approval with no out-of-hours route.

"The engineer was careless" is not a contributing condition. A blameless postmortem names system conditions that can be changed.

## The five questions the evidence answers

| Question | Evidence |
|---|---|
| What happened? | Timeline from logs, alerts, and deploy records |
| How bad was it? | 660 errors, 128 minutes, p95 and error rate from metrics |
| Why did it happen? | Missing feature in the contract; gate override; full rollout |
| Why did it take so long? | Detection at 02:12, approval at 03:52, alias at 04:20 |
| What would prevent it? | Contract test in the gate, canary, pre-approved out-of-hours rollback |

Each answer cites an artefact. None relies on memory. That is the standard the capstone's postmortem is held to.

## What a capstone defence sounds like

A weak answer:

> "We used FastAPI because it is fast, Docker for portability, and GitHub Actions for CI. The model has 0.84 AUC. The system is scalable."

A stronger answer:

> "The system predicts equipment failure for a maintenance planner; it is not used for automatic shutdown, because a false negative is a missed inspection, not a safety event. We used a single container and Compose because the p95 target is 40 ms at 20 requests per second and one node meets it; Kubernetes would add a control plane we cannot operate. The gate blocks on ROC AUC below 0.75, recall below 0.70, and any machine group missing from the training data. A clean clone takes 12 minutes on a laptop. At 10× load, the first bottleneck is the model server's single process; we would add workers before adding nodes. The top residual risk is that the labels arrive seven days late, so a quality regression is invisible for a week; we monitor input drift and the prediction distribution in the meantime."

The second answer names the decision, the trade-off, the evidence, the bottleneck, and the residual risk. That is what the defence is testing.

## What this example does not prove

- It does not prove a capstone is complete; it is a reference and a rehearsal.
- It does not prove the starter's CI works on a hosted runner; only the commands were run locally.
- It does not prove the incident's prevention items were implemented; they are recommendations.
- It does not prove the system is fair, secure, or cheap; those require the Module 15 and 16 artefacts, and the Full variant's evidence.

The capstone's value is that it makes you produce the missing evidence yourself. The example shows the shape of that evidence, not a substitute for it.

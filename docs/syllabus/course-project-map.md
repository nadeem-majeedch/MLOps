# Course Project Map

The course has one running system, built in pieces, so that every new practice is applied to something already familiar. This page is the map of that system: what exists after each module, which module consumes it, and what the final handover must contain.

If you are wondering "why am I doing this lab?", the answer is here.

---

## 1. The running case: RaviRide ETA

> **RaviRide** is a fictional ride-hailing company in Lahore. Before a rider books, the app shows an estimated arrival time. The estimate comes from a model trained on completed trips. Operations cares about it because a wrong estimate changes rider behaviour: too high and riders cancel, too low and they complain.

You build **`raviride-eta`**, a repository that starts empty in Module 02 and ends as an operated service in Module 17.

### 1.1 The data

A synthetic dataset of completed trips, generated for the course. No real riders, drivers, or locations are involved.

| Field | Type | Notes |
|---|---|---|
| `trip_id` | string | Unique; duplicates are a defect |
| `requested_at` | timestamp | Used for temporal splits; never use a random split here |
| `pickup_zone` | category | Central and peripheral zones; boundary changes mid-dataset |
| `dropoff_zone` | category | Same vocabulary as pickup |
| `distance_km` | float | Positive; negative values are a defect |
| `passengers` | integer | 1-4; affects boarding time |
| `weather` | category | `clear`, `cloudy`, `rain`, `monsoon`; monsoon conditions drive the drift lab |
| `traffic_index` | float | Upstream feed at request time; occasionally delayed or stale |
| `driver_supply` | integer | Available drivers in the zone at request time |
| `fare_amount` | float | Written by the meter **after** the trip; a leaky column, never a feature |
| `duration_min` | float | **Target**: actual trip duration in minutes |

`hour`, `day_of_week`, `is_weekend`, `is_peak`, and `log_distance` are derived in the featurise stage, not delivered in the extract.

Data is delivered in batches by module: a clean batch in 04, a corrupt batch to reject in 04, seasonal batches in 14. The generator is part of the course repository so results are reproducible. It currently produces a 1,200-row, 28-day extract from a fixed seed (`scripts/generate_trips.py`); later modules extend it with seasonal batches rather than replacing it.

### 1.2 Why this case

- **Temporal.** Splits must respect time, which exposes leakage honestly rather than as a theoretical warning.
- **Drifting.** Traffic, weather, and city boundaries change, so monitoring is not a contrived exercise.
- **Servable.** A single-record prediction is natural, so an API is a sensible deliverable.
- **Sliceable.** Central versus peripheral zones gives a genuine fairness and evaluation-slice discussion without sensitive personal attributes.
- **Ethical.** No personal data, no scoring of individuals, no high-stakes decision about a person's rights.

---

## 2. The artefact ladder

Each row is something that exists after that module and is used later. Nothing is built twice.

| Module | Artefact you add | Consumed by |
|---|---|---|
| 02 | Repository skeleton, pinned environment, first branch | Everything |
| 03 | Package layout, configuration layer, ADRs, debt register | 04-17 |
| 04 | Validated dataset, DVC-tracked version, data `README` with checksum | 05, 09 |
| 05 | DVC stage graph, deterministic training, metrics file | 06, 08, 12 |
| 06 | MLflow runs, evaluation report, recorded baseline | 07, 09, 12 |
| 07 | Four test layers, regression gate | 08, 12 |
| 08 | One-command automation, hooks, runbook draft | 09, 12, 13 |
| 09 | Registry versions, promotion policy, rollback rehearsal log | 10, 12, 16 |
| 10 | FastAPI service, contract tests, latency measurements | 11, 12, 14 |
| 11 | Dockerfile, `.dockerignore`, Compose file | 12, 16 |
| 12 | CI workflow with real gates, branch-protection recommendation | 13, 14, 17 |
| 13 | Orchestrated nightly retrain, schedule, retry policy | 14, 17 |
| 14 | Drift reports, alert rule, retraining memo | 17 |
| 15 | Threat model, scan reports, fairness table, model card | 17 |
| 16 | Manifests, Terraform plan, SLOs, cost worksheet, rollout plan | 17 |
| 17 | Integrated handover package and incident postmortem | Portfolio |

**Naming rule:** artefacts keep stable paths (`src/raviride/`, `dvc.yaml`, `Dockerfile`, `.github/workflows/ci.yml`, `docs/runbook.md`). Later modules modify these files; they do not create parallel copies. If you find yourself with `train_v2_final.py`, the project has gone wrong.

---

## 3. Progressive mini-projects

Four checkpoints where separate modules must work together. Each is worth 10% of the suggested self-assessment total; rubrics are in the [assessment framework](assessment-framework.md).

### MP1 - Reproducible training package (after Module 05)

**Brief.** A colleague clones your repository on a different machine and must obtain your reported metric without asking you anything.

**Deliverables**
1. Repository with pinned environment and documented single install command.
2. DVC-tracked dataset with provenance.
3. Stage graph (prepare, featurise, train, evaluate) that reruns correctly.
4. `metrics.json` and a two-run comparison showing identical results.
5. A `README` section a stranger can follow without prior knowledge of your choices.

**Acceptance criteria**
- A clean directory installs and trains using only documented commands.
- Two consecutive clean runs produce metrics within ±2% (state your tolerance before running).
- Changing one hyperparameter invalidates only the affected stages, demonstrated by logs.
- No absolute paths, no committed datasets, no secrets.

**Typical failure:** the run works because of an untracked file in the working directory. Test by cloning to a new folder before submitting.

### MP2 - Evaluated and registered model (after Module 09)

**Brief.** Promote one model to `champion`, and prove a worse one cannot get there.

**Deliverables**
1. Six tracked runs with parameters, metrics, and dataset version.
2. Evaluation report with at least two slice dimensions and a decision rule.
3. Registry with at least three versions and alias history.
4. Promotion policy with three measurable gates, implemented.
5. Blocked-promotion log and a timed rollback record.

**Acceptance criteria**
- Every claim in the report traces to a run identifier.
- The failing candidate is blocked automatically, not by convention.
- Rollback to the previous alias is demonstrated and timed.
- The report names one slice where the aggregate winner is worse.

**Typical failure:** selecting on the aggregate metric, then discovering the regression later in the capstone.

### MP3 - Served, containerised, gated service (after Module 12)

**Brief.** A caller can get a validated prediction from a container, and CI refuses a regression.

**Deliverables**
1. `/health`, `/predict`, `/model-info` with schema validation.
2. Contract test comparing serving features with training features.
3. Dockerfile with pinned base, non-root user, and `.dockerignore`; size comparison.
4. Compose file running the API beside the tracking store.
5. CI workflow: lint, tests, data validation, smoke train, metric gate, artefact upload.

**Acceptance criteria**
- Five malformed payloads each return 422 with a specific message.
- p95 latency is measured and stated against a budget you defined.
- Image builds from scratch on a clean machine.
- CI fails on a data-schema break, a unit regression, and a metric regression - each for the stated reason.

**Typical failure:** a gate that passes because the baseline file was regenerated by the same failing run. Pin the baseline.

### MP4 - Monitored lifecycle (after Module 14)

**Brief.** The system notices its own degradation and proposes a retrain, with evidence.

**Deliverables**
1. Drift report per batch across four weeks of replayed data.
2. Thresholds with justification, and an alert with an owner and first diagnostic step.
3. A retraining trigger that is conditional, not unconditional.
4. Before/after comparison showing improvement on the affected slice and no regression elsewhere.
5. A one-page decision memo for a non-technical manager.

**Acceptance criteria**
- Data drift is distinguished from prediction drift in the report.
- The alert fires on the injected drift batch and not before it.
- Retraining is justified by evidence, and the guardrail prevents auto-promotion of a worse model.
- The memo states the cost of the retrain and the cost of not retraining.

**Typical failure:** thresholds chosen to look strict, producing an alert on every batch - which is the same as no alert.

---

## 4. Project time

| Item | Hours | Where it sits |
|---|---|---|
| Guided labs | Inside each module's effort | Modules 01-16 |
| Mini-projects (4) | ~40 total | After modules 05, 09, 12, 14 |
| Capstone | 48 | Module 17 |

The 284-hour total in the [course overview](course-overview.md) includes the capstone and allows the mini-projects inside the 10-20% independent-work margin. Do not treat the mini-projects as optional extras; they are where integration is learned.

---

## 5. Capstone requirements: what is assessed

Two variants exist. Choose **Core** if you completed the essential path; choose **Full** if you also completed Modules 13, 15, and 16.

| | Core capstone | Full capstone |
|---|---|---|
| Modules required | Essential path | All modules |
| Orchestration | Script plus Task Scheduler acceptable | Prefect flow with retries |
| Deployment | Local process or Compose | Local cluster with probes and limits |
| Security artefacts | Threat model and secret scan | Plus dependency scan, fairness analysis, access sketch |
| Expected effort | ~35 hours | ~48 hours |

### 5.1 Required artefacts

1. **Rerunnable pipeline.** A clean clone installs, validates data, trains, evaluates, and reports a metric using documented commands.
2. **Versioned data and model** with provenance from dataset hash to registered version to deployed alias.
3. **Automated tests and a CI gate** that demonstrably blocks a data, code, and metric regression.
4. **Served endpoint** with schema validation, contract tests, and a documented latency budget.
5. **Monitoring** with at least four signals, a justified threshold, and an alert naming an owner and first action.
6. **Runbook** covering deployment, rollback, and the top three alerts, written for someone who is not you.
7. **Model card and defence document**, including limitations and residual risk.

### 5.2 Measurable acceptance criteria

A capstone passes when all of the following are true. Each is checkable by someone else in under ten minutes.

- [ ] A clean clone reaches the reported metric within the stated tolerance, following only the `README`.
- [ ] CI fails for the correct stated reason on three injected regressions (schema, unit, metric), evidenced by logs.
- [ ] Rollback from the current champion to the previous version is demonstrated and takes under five minutes.
- [ ] At least five malformed prediction requests return 422 with specific messages.
- [ ] The alert fires on the injected drift batch and includes an owner and a first diagnostic step.
- [ ] A peer who has not seen the project deploys it from the runbook in under 30 minutes.
- [ ] `gitleaks` (or equivalent) reports no unaddressed findings.
- [ ] The model card states at least two limitations and the measured disparity between central and peripheral zones.
- [ ] The incident simulation is diagnosed within 30 minutes, with the evidence path recorded.
- [ ] The defence answers "why not simpler?" and "what breaks at ten times the load?" with specifics.

### 5.3 Handover package

```text
capstone/
├── README.md              # what it is, how to run it, what it does not do
├── docs/
│   ├── architecture.md    # diagram plus the two decisions that shaped it
│   ├── runbook.md         # deploy, rollback, top three alerts
│   ├── model-card.md      # intended use, limitations, disparity, monitoring
│   └── postmortem.md      # injected incident: timeline, cause, controls
├── evidence/
│   ├── ci/                # green and correctly-red run logs
│   ├── drift/             # reports and the alert that fired
│   └── rollback/          # timed log
└── <the working system>
```

The `evidence/` directory matters more than it looks. It is the difference between claiming a gate works and showing it.

### 5.4 Incident simulation

At the end of the capstone, a fault is injected without warning: a stale model alias, a corrupted feature, a missing dependency, or a failed rollback. You must:

1. Detect it from your own monitoring or a reported symptom.
2. State a hypothesis and the first diagnostic step, before touching anything.
3. Gather evidence that confirms or rejects the hypothesis.
4. Restore service, using the runbook where possible.
5. Write a postmortem: timeline, cause, why detection took as long as it did, and one control to add.

If you are studying alone, use the supplied fault-injection script and a timer. The discipline of a clock is the point.

---

## 6. Using your own data instead

You may substitute a dataset you have the right to use, if it satisfies all of these:

- **No personal or sensitive data**, and no data you cannot legally redistribute or process.
- **Temporal or grouped structure**, so splitting is a real decision rather than a formality.
- **A plausible operational context**: someone acts on the prediction, and being wrong has a cost.
- **Small enough to run on a laptop** (under about 500 MB).
- **A licence that permits educational use**, recorded in your data `README`.

Keep every artefact and acceptance criterion identical. The assessment is about the system, not the dataset, and substituting a dataset does not reduce the work.

---

## 7. Common ways projects fail

| Failure | What it looks like | Prevention |
|---|---|---|
| Rebuilding instead of extending | `train_new.py`, `train_final_v2.py` | Keep the artefact ladder; modify files in place |
| Untracked state | Works locally, fails on clone | Rehearse the clean clone at every mini-project |
| Gate theatre | CI is green but checks nothing meaningful | Inject a deliberate regression and watch it fail |
| Metric tunnel vision | Aggregate improves, a slice collapses | Slice metrics are required from Module 06 onward |
| Documentation afterthought | Runbook written in the final hour, untested | Write it in Module 08 and update it each module |
| Silent substitution | Faster path used in the lab, different path reported | Report exactly what was run, including the reduced path |
| Scope explosion | Adding tools not in the course | One new tool per module; the capstone adds none |

---

## 8. Portfolio narrative

At the end of the capstone, write 400-600 words answering:

1. What does the system do, and for whom?
2. What would have gone wrong if you had skipped Modules 04, 07, and 14?
3. Which decision are you least confident about, and what evidence would change your mind?
4. What would you do first if this had real users next week?

This is the document you would attach to a job application, and the one you would reread before an interview. It is assessed as part of the defence, not for polish but for specificity.

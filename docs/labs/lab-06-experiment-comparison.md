# Lab 06 · Compare four experiments without trusting your memory

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L06 | Intermediate | 3 hours | [06 · Experiment tracking](../modules/06-experiment-tracking/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-06-experiment-comparison/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-06-experiment-comparison) — starter files, data generator, and acceptance checker.

## Scenario

Four configurations were trained last week. A spreadsheet holds the MAEs, and
the person who ran two of them is on leave. The spreadsheet says "deep" won by
0.006, which is inside the noise of the pipeline from Lab 05, and it says nothing
about which learner group got worse.

You will make each run describe itself: parameters, data hash, per-section
metrics, and the model artefact. Then you will write the comparison as code so
the ranking is derived from the store rather than from a spreadsheet.

## What you will be able to do

- Log the parameters and tags a comparison actually needs.
- Log slice metrics, not only the aggregate.
- Query a tracking store and build a decision table from it.
- Say what a 0.006 difference does and does not justify.

## Prerequisites and setup

```bash
cd examples/labs/lab-06-experiment-comparison
python ../_shared/make_sessions.py --out data/sessions.csv
python experiments.py
```

MLflow writes to a local `mlruns/` directory. No server, no account.

## Your task

Complete the four TODOs in `experiments.py` and implement `compare.py`. The
checker verifies both the store contents and the comparison output.

## Data and starter files

| File | Purpose |
|---|---|
| `experiments.py` | Four configs, currently logging only `mae` |
| `compare.py` | Skeleton: must produce the decision table |
| `check_lab06.py` | Inspects the MLflow store, then validates the comparison |

Configurations: `baseline` (120 trees, depth 8), `deep` (300, 14), `shallow`
(60, 4), `no_sleep` (120, 8 without `sleep_hours`).

## Steps

### 1. Log what changes the model

Every run needs `trees`, `depth`, `features`, `seed` and `train_rows` as
parameters, plus `data_hash` and `code_version` as tags. A run without these is a
number with no provenance.

### 2. Log slices, not just the mean

Compute MAE per section (`A`, `B`, `C`) as `mae_section_A` and so on, plus
`rmse`, `r2` and `p95_abs_error`. The aggregate can improve while a slice
degrades; without slice metrics you cannot see it.

### 3. Log the model

`mlflow.sklearn.log_model(model, artifact_path="model", signature=..., input_example=...)`.
The check verifies that `model/MLmodel` exists for every run, because a metric
without the artefact cannot be re-examined.

### 4. Build the comparison

`compare.py` must query the experiment, sort by MAE, and return:

```json
{"experiment": "lab06-comparison",
 "best": {"run_name": "deep", "mae": 4.8704},
 "weakest_slice": {"run_name": "deep", "slice": "B", "mae": 5.4319, "relative": 0.1153},
 "table": [{"run_name": "deep", "mae": 4.8704, "mae_section_A": 4.51, "mae_section_B": 5.43, "mae_section_C": 4.62}]}
```

Read it from the client, not from the experiment script's printed output.

### 5. Run the checker

```bash
python check_lab06.py
```

Expected: `15/15 checks passed`. The checker clears `mlruns/` first, so it always
starts from an empty store.

## Expected output

Reference values from the course environment:

```text
best run is the lowest MAE in the store -- got 'deep', expected 'deep'
best MAE matches the store -- got 4.8704, expected 4.8704
weakest slice is the worst section of the best run -- got 'B', expected 'B'
weakest slice MAE matches the store -- got 5.4319, expected 5.4319
weakest slice is reported relative to overall MAE -- relative=0.1153
```

The ranking is re-derived from whatever your runs produce; the checker does not
hard-code `deep`.

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Four runs exist | 4 |
| 2 | Each run has the four parameters | `trees`, `depth`, `features`, `seed` |
| 3 | Each run has per-section metrics | Three `mae_section_*` keys |
| 4 | Each run has data and code tags | `data_hash`, `code_version` |
| 5 | Each run stores a model artefact | `model/MLmodel` |
| 6 | Best run matches the store's lowest MAE | Exact name and value |
| 7 | Weakest slice matches the store | Name and value |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Experiment not found | Tracking URI relative to a different cwd | Use `Path("mlruns").resolve().as_uri()` |
| Runs accumulate across attempts | Store not cleared | Delete `mlruns/` before a clean comparison |
| `mlflow.log_metric` rejects a value | numpy float | Cast with `float(...)` |
| Model artefact missing | Logged model outside the run context | Call `log_model` inside `with mlflow.start_run()` |
| Comparison picks the wrong best run | Sorted by `start_time` | Sort by `metrics.mae ASC` in the query |

## Reflection questions

1. The best MAE is 0.09 better than the baseline. Given Lab 05's noise, what
   would you need before recommending a change?
2. What does a weak section tell you that a weak overall metric does not?
3. Why log the data hash as a tag rather than as a parameter?
4. Which of these four runs would you promote if section B were the largest
   traffic segment?

## Optional extension

Add a fifth configuration that trains only on sections A and B, then use
`compare.py` to show that its overall MAE improves while section C disappears
from the report. That is the failure mode Lab 08 blocks.

## Cleanup

```bash
rm -rf mlruns artifacts data
```

PowerShell: `Remove-Item mlruns, artifacts, data -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] Every run logs its parameters, data hash and code version
- [ ] Every run logs per-section MAE
- [ ] Every run stores a loadable model artefact
- [ ] The comparison is computed from the store, not pasted
- [ ] `check_lab06.py` reports `ACCEPTED`

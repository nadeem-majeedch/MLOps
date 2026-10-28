# Guided lab · Track six runs, then find the weakness

**Time:** 5 hours. **Tools:** Python 3.11/3.12, scikit-learn, MLflow (local tracking, no server). CPU only.

## Scenario and business problem

The team has six candidate ETA models and a spreadsheet column called "MAE". The product manager asks a fair question: *if we ship the best one, who does it fail?* Nobody can answer, because nobody has looked inside the aggregate.

You will track the six runs, produce a comparison that a reviewer can check, and then do the part that matters: find the slice where the winner is worst, quantify it, and write a recommendation that says what you would defend.

### Skills practised

- Logging parameters, metrics, tags, and artefacts.
- Querying and comparing runs.
- Designing slice metrics and reporting their sample sizes.
- Recording a baseline that later automation can compare against.
- Writing a selection note with caveats.

### Prerequisites

Modules 02–05. A working `dvc repro` pipeline, `data/features/{train,test}.csv`, and a model artefact.

### Input data

The feature files produced by your pipeline (304 test rows, 896 train rows). No downloads, no accounts.

### Directory layout

```text
raviride-eta/
├── experiments/track_runs.py
├── mlruns/                     # tracking store, ignored by Git
├── baseline.json               # recorded from an accepted run
└── docs/evaluation-report.md
```

## Part 1: configure the store (20 minutes)

1. Install MLflow into your environment and record the version:
   ```powershell
   python -m pip install "mlflow==2.17.2"
   python -c "import mlflow; print(mlflow.__version__)"
   ```
   **Checkpoint 1:** the version prints. If installing the full package is slow or blocked on your network, `mlflow-skinny` provides the tracking API; the UI will be unavailable, which is noted below.
2. Add `mlruns/` to `.gitignore`. The store is generated state.
3. Point the tracking URI at a project-local directory before any logging, then set the experiment name.

## Part 2: log the six variants (90 minutes)

4. Write `experiments/track_runs.py` with the six variants from the [worked example](worked-example.md#the-experiment-loop).
5. For each run, log:
   - parameters: `feature_set`, `n_estimators`, `max_depth`, `min_samples_leaf`, `random_state`, `train_rows`
   - tags: `data_hash` (first 16 hex characters of the SHA-256 of both feature files), `test_start`, `test_end`
   - metrics: `mae`, `rmse`, `r2`, `p95_abs_error`, `mae_peak`, `mae_off_peak`, `mae_zone_Z01` … `mae_zone_Z08`
   - artefact: the fitted model
6. Run it:
   ```powershell
   python experiments/track_runs.py
   ```
   **Checkpoint 2:** six runs exist in the `raviride-eta` experiment, and the script prints one line per run with MAE and R².

*Recovery:* if a run appears with no metrics, the logging call was inside the `with` block but after an exception; check the artefact logging line, which is the usual failure point (signature warnings are harmless).

## Part 3: compare (45 minutes)

7. Query the runs and print the comparison table from the worked example.
8. **Checkpoint 3:** your table has six rows, sorted by MAE, with the peak and p95 columns.
9. Export it to CSV for the report:
   ```python
   runs.to_csv("docs/run-comparison.csv", index=False)
   ```
10. Answer in `docs/evaluation-report.md`: which factor moved MAE more, feature set or model size? Support it with two specific numbers from your table.

## Part 4: slice analysis (60 minutes)

11. For the two best runs, produce a per-zone table with MAE and test row count.
12. **Checkpoint 4:** you can name the zone with the worst error and state how many rows it is based on.
13. Compute the peak and off-peak MAE for the winner and express the ratio ("peak error is 1.x times off-peak").
14. Write the three findings section of the report: the worst slice, whether the runner-up is better anywhere, and what the slice sizes mean for confidence.

## Part 5: baseline and recommendation (45 minutes)

15. Choose the model you would ship *today* and copy its metrics into `baseline.json`:
    ```powershell
    Copy-Item metrics.json baseline.json
    ```
    (Adjust if your evaluate stage writes the metrics for the selected variant.) Record in the report why this run and not the one with the lowest MAE, if they differ.
16. Write the recommendation using the worked example's structure: recommendation, evidence, caveats with numbers, next question.
17. State the selection rule you used, and how many comparisons it involved.

## Expected outputs

| Output | Reference values |
|---|---|
| Runs | 6, with parameters, tags, metrics, artefact |
| Best aggregate | `rf_full_deep`: MAE 2.661, RMSE 5.002, p95 8.603 |
| Worst slice | Z08: 6.52 min on 17 rows (runner-up 7.42) |
| Peak vs off-peak | 4.118 vs ~2.3 min |
| Baseline | `baseline.json` with an `overall.mae` field |
| Report | Recommendation with caveats and a stated selection rule |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Traceability | Every run has a dataset hash tag and a retrievable model artefact |
| Comparability | All runs used the same split; you state how you know |
| Slice honesty | Slice metrics include row counts, and the smallest slice is flagged |
| Decision | The recommendation names a model, a reason, and at least two caveats with numbers |
| Baseline | A file that Module 07's gate can read without modification |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `mlflow ui` fails with `ModuleNotFoundError: flask` | Only `mlflow-skinny` installed | Install full `mlflow`, or use `search_runs` as the comparison view |
| Runs appear in `./mlruns` next to the script | Tracking URI not set before logging | Set it once at startup from `PROJECT_ROOT` |
| Two experiments with the same name | Different tracking URIs | Use one local store per project; check `mlflow.get_tracking_uri()` |
| Model logging warns "without a signature" | No `input_example` passed | Expected here; Module 10 adds request validation |
| Metrics missing on one run | Exception after logging params | Wrap the run body so a failure is visible; do not swallow it |
| Table sorted oddly | Column is a string in `search_runs` output | Metrics are floats; check you selected the `metrics.` prefix |

## Cleanup

- Keep `mlruns/` locally for inspection; it is ignored by Git. If it grows, remove experiments you no longer need through the UI or API, not by deleting files under a running server.
- No services were started, so nothing needs stopping.

## Optional extensions

1. **Nested runs.** Group the six variants under one parent run, log the comparison table as a parent artefact, and explain what the nesting buys.
2. **Uncertainty.** For the winning model, bootstrap the test set 200 times and record the 95% interval of MAE as a metric. Does the difference between 2.661 and 2.777 survive it?
3. **Second experiment.** Change one preprocessing decision (for example, log-transform the target) in a new experiment, and compare across experiments. Explain why cross-experiment comparison needs the same test rows and the same tags.

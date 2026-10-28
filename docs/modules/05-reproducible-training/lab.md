# Guided lab · Build the four-stage pipeline

**Time:** 5 hours. **Tools:** Python 3.11/3.12, DVC 3.x, Git. Local disk only.

## Scenario and business problem

The ETA model now trains reproducibly by hand, one command per stage. That is still a person remembering an order. The team wants a single command that runs whatever is stale, and no work when nothing changed: the data team retrains often, and a 15-minute experiment that reruns a 10-minute preparation step is a 15-minute experiment nobody repeats.

You will also be asked a question that sounds trivial and is not: *if I change one hyperparameter, what reruns?* Your answer has to be right before you run, not after.

### Skills practised

- Declaring stages, dependencies, parameters, and outputs.
- Reading and predicting cache invalidation.
- Making a training entry point deterministic and idempotent.
- Separating a stateful model from a stateless feature function.
- Measuring stage cost.

### Prerequisites

Modules 02–04, including the DVC remote and a dataset tracked with `dvc add`.

### Input data

`data/raw/trips.csv` (1,200 rows), tracked by DVC from Module 04. If you are starting fresh, regenerate it with the course generator; the checksum in `data/raw/trips.csv.dvc` must match.

### Directory layout

```text
raviride-eta/
├── dvc.yaml
├── dvc.lock
├── params.yaml
├── data/processed/{train,test}.csv
├── data/features/{train,test}.csv
├── models/{model.joblib,run_meta.json}
├── metrics.json
└── src/raviride_eta/{prepare,featurise,train,evaluate}.py
```

## Part 1: make the stages deterministic (60 minutes)

1. Ensure every stage is runnable with `python -m raviride_eta.<stage>` and does its work inside `main()`.
2. Set `random_state` from `params.yaml` and pass it to `RandomForestRegressor`. Set `n_jobs=1` so timings and floating-point reduction are comparable between runs.
3. Sort the frame by `requested_at` after loading and before splitting, then reset the index.
4. Run the sequence twice and compare:
   ```powershell
   python -m raviride_eta.prepare; python -m raviride_eta.featurise
   python -m raviride_eta.train; python -m raviride_eta.evaluate
   (Get-FileHash models/model.joblib -Algorithm SHA256).Hash
   ```
   **Checkpoint 1:** run the block again; the hash and the MAE are unchanged. If they differ, find the source before adding DVC - a pipeline caches nondeterminism just as faithfully.

## Part 2: declare the pipeline (90 minutes)

5. Write `dvc.yaml` with the four stages from the [worked example](worked-example.md#the-stage-graph). Include every source file the stage imports in `deps`; a missing import is a hidden input.
6. Add `features.set` to `params.yaml` and to the `train` and `evaluate` params lists.
7. Run:
   ```powershell
   dvc repro
   ```
   **Checkpoint 2:** all four stages run, in order, and `dvc.lock` is created. Commit `dvc.yaml` and `dvc.lock` together.

*Recovery:* if a stage fails with `ModuleNotFoundError`, DVC used a different interpreter - activate the environment in the same shell. If it fails with a path error, your stage used the current working directory instead of `config.PROJECT_ROOT`.

## Part 3: predict, then confirm, the cache (45 minutes)

8. Write your prediction in `docs/pipeline-evidence.md` as a table: change → stages you expect to rerun.
9. Run `dvc repro` with no changes.
   **Checkpoint 3:** `Data and pipelines are up to date.`
10. Change `model.n_estimators` from 200 to 120 and run `dvc repro`.
    **Checkpoint 4:** exactly `train` and `evaluate` run; the metrics change slightly (reference: MAE 2.777 → 2.787).
11. Restore 200, rerun, and confirm the original metrics return. This also proves the cache is content-based, not "last result wins".
12. Delete `data/processed/` and run `dvc repro`.
    **Checkpoint 5:** `prepare` and `featurise` are *cached* and their outputs are checked out, rather than recomputed. Explain in your evidence file why this is possible and why it is not the same as "the stage ran".

## Part 4: add a feature and watch the graph (45 minutes)

13. Add one derived feature to `features.py` (for example `is_weekend_night` or `distance_per_passenger`). Add it to the `full` feature set.
14. Predict which stages will rerun before running.
    **Checkpoint 6:** `featurise`, `train`, and `evaluate` rerun; `prepare` does not. If `prepare` reran, you listed `features.py` as one of its dependencies by mistake - a good illustration of how a wrong `deps` entry over-invalidates.
15. Record the metric change. If the feature does not help, say so and remove it; a pipeline that makes experiments cheap should also make it easy to discard them.

## Part 5: measure and document (30 minutes)

16. Time a fresh run (`Remove-Item -Recurse -Force .dvc\cache` first) and a cached run:
    ```powershell
    Measure-Command { dvc repro }
    ```
17. Record per-stage durations from the fresh run (the stage output prints are enough; `dvc.lock` records timings).
18. Export the DAG with `dvc dag --mermaid` and paste it into the evidence file.
19. Commit. The evidence file should contain: the prediction table, the three run outputs, timings, the DAG, and one paragraph on what remains non-deterministic.

## Expected outputs

| Output | Reference value |
|---|---|
| Fresh run | four stages, MAE 2.777, RMSE 5.259, R² 0.8298 |
| Cached run | `Data and pipelines are up to date.` |
| Parameter change | `train` + `evaluate` only; MAE 2.787 at 120 trees |
| Model hash, two runs | identical SHA-256 |
| DAG | raw → prepare → featurise → {train} → evaluate |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Determinism | Two runs give identical metrics; artefact hash identical or the difference explained |
| Declaration | Every file a stage reads is in `deps`; every value it reads is in `params` |
| Prediction | Your expected-rerun table matches the observed runs |
| Reuse | The feature function is callable on a single row with the same result as on the batch |
| Evidence | The evidence file contains real outputs, timings, and the DAG |
| Hygiene | `dvc.lock` is committed; generated data is not in Git |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Stage 'x' didn't change` but you changed a file | File not listed in `deps` | Add it, then `dvc repro` |
| Everything reruns every time | A dependency changes on each run (timestamp, log file) | Remove the volatile file from `deps`; write it outside the project |
| `dvc repro` says outputs are missing, then skips | Outputs deleted but cache intact | Expected: DVC checks out from cache. Use `--force` to truly rerun |
| `PermissionError` on `models/` | Stage run from the wrong directory | Anchor paths to `PROJECT_ROOT` |
| Metrics identical after a parameter change | Parameter not listed in `params`, or hard-coded | Add to `dvc.yaml` and read it from `load_params()` |
| `dvc.lock` merge conflict | Two people repro'd different versions | Resolve by rerunning `dvc repro` on the merged `dvc.yaml`; never hand-merge hashes |

## Cleanup

- `dvc push` after the final run so the cache is recoverable.
- Remove scratch timing files.
- No services were started.

## Optional extensions

1. **Skip a stage deliberately.** Use `dvc repro --single-item train` to rerun one stage. Read `dvc repro --help` and explain in one sentence when this is safe and when it desynchronises the pipeline.
2. **Second dataset version.** Change `data.test_days` to 10, rerun, and record which stages rerun. Then explain why the metric is not comparable to the previous one (different question, not worse model).
3. **Stage signature.** Add a `--predict-file` option to `train` that writes one prediction for a fixed input row. Run it before and after a retrain and compare. This is the beginning of the serving contract in Module 10.

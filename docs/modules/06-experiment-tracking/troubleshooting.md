# Troubleshooting · Module 06

## The user interface

**`mlflow ui` fails with `ModuleNotFoundError: flask`.** You have `mlflow-skinny`, which provides the tracking API without the web UI. Install the full package (`pip install mlflow`) if you want the UI; the API, `search_runs`, and artefact logging work without it. This course's comparison examples use `search_runs` for that reason.

**The UI shows no runs.** It is reading a different store. Compare `mlflow.get_tracking_uri()` in your script with the `--backend-store-uri` you passed to `mlflow ui`. Both must resolve to the same directory.

**Port already in use.** `mlflow ui --port 5001`. Do not kill a process by name; find the PID that owns the port.

## The store

| Symptom | Cause | Fix |
|---|---|---|
| Runs land in an unexpected folder | URI not set before the first logging call | Set the tracking URI at import time, from `PROJECT_ROOT` |
| `MlflowException: Run with UUID ... is already active` | Nested `start_run` without `nested=True` | End the parent run, or nest explicitly |
| Two experiments with one name | Different stores, or the name was deleted and recreated | Keep one store; check the experiment ID, not only the name |
| Registry commands fail on a file store | Model registry needs a database backend | Expected locally; Module 09 moves to SQLite or a server |
| `mlruns/` in Git | Ignore rule missing | Add it, `git rm --cached -r mlruns` |

## Logging

**"Model logged without a signature and input example."** A warning, not an error. The model is usable; the signature is what lets a serving layer validate request order and types. Module 10 adds that at the API boundary, and passing `input_example=` here would record it earlier.

**Metrics missing from a run.** An exception after `log_params` leaves a run with parameters only. Wrap the body so failures surface; an empty run in a comparison table is a silent trap.

**Artefact path errors on Windows.** Use a relative `artifact_path="model"`; absolute paths outside the store can be recorded as links that other machines cannot read.

**Parameters logged as strings.** `log_params` stores values as given; `"12"` and `12` sort differently. Pass numbers as numbers.

## Comparison

- `search_runs` returns columns prefixed by kind (`metrics.mae`, `params.max_depth`, `tags.mlflow.runName`). Selecting `mae` returns nothing.
- Sorting by a metric that some runs lack puts those runs last, not first. Check for empty cells before concluding a run was bad.
- Comparing runs from different experiments is allowed and usually misleading. Compare only runs with the same `data_hash` and the same test window.

## When the numbers disagree with the lab

If your MAE differs from the reference values, the cause is almost always the split: a different cutoff, a different dataset generation seed, or a feature file regenerated after a parameter change. Check the dataset hash tag on the run before questioning the model.

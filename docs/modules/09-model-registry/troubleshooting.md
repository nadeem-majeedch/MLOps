# Troubleshooting · Module 09

## Diagnose in this order

1. **Which version?** Print the alias target before anything else. Most registry confusion is a version mismatch, not a bug.
2. **Which store?** `mlflow.get_tracking_uri()` inside the failing process. Two processes with different URIs see two different registries.
3. **Which run?** The version stores a `run_id`; metrics live there, not on the version.
4. **Which data?** The run's `data_hash` and `train_rows`. A mismatch here explains most "the model got worse" reports.

## Failure table

| Symptom | Likely cause | Fix |
|---|---|---|
| `RESOURCE_DOES_NOT_EXIST: Model version not found` | Wrong model name, wrong tracking URI, or a version registered in a different store | Print both; use an absolute `file:` URI |
| `Alias champion not found` | No promotion yet | Promote a version, or handle the empty-champion case in the gate |
| `get_model_version_by_alias` missing | MLflow version too old | Use 2.x; do not fall back to stages |
| Version registered but metrics empty | Metrics logged in a different run, or after the run closed | Query the version's `run_id`; log metrics inside `with mlflow.start_run()` |
| `ModuleNotFoundError` when loading the model | The artifact needs the training package | Save the pipeline, not a custom class; test loading in a clean environment |
| Signature mismatch on load | Feature frame order or dtypes differ from training | Reuse `feature_columns(set_name)`; do not hand-build the list |
| Model predicts nonsense after promotion | Preprocessing not saved with the estimator, or a different feature set | Compare a single prediction against the training pipeline |
| `PermissionError` on `mlruns/` | Files owned by another process or a container user | Fix ownership; do not run the registry as root |
| Alias moves but serving returns old predictions | Server caches the model at start-up | Reload the model or restart the service; Module 10 covers reloading |
| Rollback says `no previous champion` | `promoted_from` absent (first promotion) | Pass `--to VERSION` |

## Case 1: "the alias moved but the metric did not improve"

Check three things in order:

```python
client.get_model_version_by_alias("raviride-eta", "champion").version
client.get_run(version.tags["run_id"]).data.metrics
```

- The version changed, but the run's metrics are the old ones: the promotion compared stale metrics because the gate read a cached JSON file instead of the run.
- The version did not change: the promoter swallowed the gate result. Search for `if not ok: return 0`.
- Both changed, and the metric is genuinely better on your test set: the serving path may not use the new artifact.

## Case 2: "the model will not load on the server"

This is the most common production failure and it is not a registry problem.

```text
ModuleNotFoundError: No module named 'raviride_eta'
```

The artifact was saved by a custom class or a function defined in your package. Options:

1. Save a plain `Pipeline` of library components (the reference approach).
2. Package the code as an installable dependency and pin its version in the serving image.
3. Use a flavour that records the code path (`mlflow.pyfunc` with `code_path`), accepting the coupling.

Test the load in the environment that will serve, not the one that trained. Module 11 makes that environment explicit.

## Case 3: gates pass locally and fail in CI

Different data, different champion, or different policy.

```powershell
git diff promotion_policy.yaml
python registry/registry.py show
```

CI usually starts with an empty registry, so "champion" does not exist and the relative gate has nothing to compare against. Decide deliberately: either seed a baseline version in CI, or make the first promotion absolute-only and document it.

## Case 4: two people promoted at once

With a file-store registry, there is no transaction. The last write wins, and neither person sees the other's decision. Symptoms: the alias points at a version nobody remembers promoting; `promoted_from` does not match the actual previous champion.

This is a limitation, not a bug to fix in your script. Use a server-backed registry for concurrent teams, or serialise promotions through one automation account (Module 12).

## Case 5: an old version's metrics changed

They cannot, if the run was closed and the store is intact. What usually happened: someone overwrote `metrics.json` in the working tree, and a report read the file rather than the run. Read metrics from the run, not from a mutable file, whenever you are making a decision about a version.

## When to stop debugging

If two sources disagree about which model is live, stop and establish one source of truth before fixing anything else. In this course that source is the alias; in your organisation it may be a deployment manifest. Either is fine. Two is an outage waiting for a reason.

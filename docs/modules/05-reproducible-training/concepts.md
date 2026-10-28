# Concepts · Module 05

## 1. Determinism, reproducibility, replicability

Three words that are often used interchangeably and should not be:

| Term | Means | Test |
|---|---|---|
| Deterministic | Same input, same output, always | Run twice on one machine |
| Reproducible | Someone else, with your code, data, params, and environment, gets the same result | Run on a clean clone, or another machine |
| Replicable | Someone else, with new data collected the same way, gets a consistent conclusion | Requires a second dataset |

MLOps is mostly about the first two. Replicability is a research property, and no pipeline can guarantee it.

### Where nondeterminism comes from

| Source | Example | Control |
|---|---|---|
| Unseeded randomness | `train_test_split` without `random_state` | Pass a seed everywhere |
| Hash-order iteration | Sets and dict ordering in feature loops | Sort before iterating |
| Parallel float reduction | Multi-threaded tree building | `n_jobs=1`, or accept metric drift |
| Time | `datetime.now()` in a filename or feature | Inject a fixed timestamp |
| Environment | Different NumPy/BLAS builds | Pin versions; record them |
| Data order | Reading a directory without sorting | Sort paths explicitly |

Two practical rules follow. **Seed at the entry point, not deep inside**: one `random_state` in `params.yaml` passed down. And **treat row order as data**: sort by a stable key after loading, before splitting, so a different file order cannot change the split.

## 2. From scripts to stages

A **stage** is a command with declared inputs, outputs, and parameters. Declaring them is what makes caching and ordering possible.

```yaml
stages:
  prepare:
    cmd: python -m raviride_eta.prepare
    deps: [data/raw/trips.csv, src/raviride_eta/prepare.py, src/raviride_eta/data.py]
    params: [data.test_days, data.window_start, data.window_end]
    outs: [data/processed/train.csv, data/processed/test.csv]
```

The four fields are the whole idea:

- `cmd` is what runs.
- `deps` are files whose content affects the output.
- `params` are values from `params.yaml` that affect the output.
- `outs` are files the stage produces, which DVC caches (and can push to a remote).

A dependency that is missing from `deps` is a **hidden input**. It is the most common pipeline bug: the stage is not rerun when the thing it reads changes, and the output silently belongs to an older world.

## 3. Cache keys and invalidation

DVC computes, for each stage, a hash over: the command, the hashes of the dependencies, the parameter values, and the hashes of the outputs. That is the **cache key**. If the key matches a cached entry, the stage is skipped and its outputs are checked out.

```text
dvc repro after changing model.n_estimators:
  prepare    did not change, skipping
  featurise  did not change, skipping
  train      running  (params changed)
  evaluate   running  (dependency artefact changed)
```

That is real output from the reference project. Predict it before running: `prepare` depends on raw data and `data.*`; `train` depends on `model.*`; `evaluate` depends on the model artefact. A parameter only invalidates stages that declare it.

**Invalidation is a feature, not an inconvenience.** It is the machine telling you which results became stale. The failure mode it prevents: retraining with a new parameter but reporting an old evaluation because the evaluation stage never reran.

## 4. Idempotency

A stage is **idempotent** if running it twice on the same inputs leaves the same outputs. This is why stages write whole files rather than appending, and why a metric file is rewritten completely on each run.

Appending is the classic violation: `metrics.jsonl` grows, and "the latest line" depends on how many times the stage ran. If you need history, that is an experiment tracker's job (Module 06), not a log file's.

## 5. Feature transformers and train/serve consistency

Module 01 introduced training/serving skew. The structural fix is to compute features in one place that both paths call:

```python
def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["requested_at"] = pd.to_datetime(out["requested_at"])
    out["hour"] = out["requested_at"].dt.hour
    ...
    return out
```

At serving time, the same function is called on a one-row frame. This works only if the function is **stateless**: no dependence on the size of the frame, no `groupby` over the batch, no filling with a column mean computed from the data at hand. Any statistic learned from data belongs in the fitted pipeline, not in a free function, so that it travels with the model artefact.

The test for statelessness: call it on one row and on the whole frame; the row's features must be identical.

## 6. Artefacts and signatures

An **artefact** is the serialised object plus the metadata needed to use it. For scikit-learn, `joblib.dump` writes the pipeline; the pipeline includes the fitted imputers, encoders, and model, which is what makes one-row prediction work.

A **signature** describes the input schema the artefact expects: column names, types, order. Without one, a caller can pass columns in the wrong order and receive plausible, wrong numbers. Scikit-learn does not enforce signatures by default; MLflow (Module 06) records them, and Module 10 adds request validation at the API boundary.

## 7. Baselines

Before comparing models, record what "good" means on this dataset with a trivial method. Two baselines are enough:

- **Constant**: predict the training median duration. For this dataset that is around 20 minutes, and it makes any model that cannot beat it obviously broken.
- **Simple**: a linear model on distance and passengers.

A baseline is not there to be beaten impressively; it is there to catch a pipeline that silently trains on the wrong column. If a sophisticated model loses to the constant baseline, the bug is in the pipeline, not the model.

## 8. The cost of a stage

Record wall-clock time per stage. Two reasons: caching decisions become informed ("this stage costs 40 seconds, so rerun it rather than debug the cache"), and regressions become visible ("prepare went from 2 s to 90 s after the join changed").

DVC records stage timings in `dvc.lock` alongside hashes. For a simple comparison:

```powershell
Measure-Command { dvc repro }
```

Compare fresh and cached runs. The difference is your cache's value, measured rather than assumed.

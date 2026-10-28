# Concepts · Module 06

## 1. The four things a run must record

A **run** is one execution of training. An **experiment** is a named group of runs that answer the same question. Within a run:

| Kind | Example | Rule |
|---|---|---|
| Parameter | `max_depth=12`, `feature_set=full` | Inputs you chose; comparable across runs |
| Metric | `mae=2.777`, `p95_abs_error=8.977` | Outputs you measured; numbers only |
| Tag | `data_hash=847fa5b8`, `git_sha=a1b2c3d` | Context that is not a number and not a choice |
| Artefact | `model/`, `metrics.json` | Files the run produced |

The distinction between parameters and tags is the one people get wrong. A parameter is something you *set* to compare alternatives. A tag describes the conditions: the commit, the dataset hash, the environment. You do not choose a commit to optimise a metric, so it is not a parameter.

**Why a spreadsheet fails.** Not because it is inelegant, but because it is unenforced: nothing records the artefact, nothing links a row to the code and data that produced it, and nothing stops two people editing the same file. The first question after a surprising result - "which commit was that?" - has no answer.

## 2. Local tracking is real tracking

MLflow's default local mode stores runs in a directory (`mlruns/`) and models as files. No server, no database, no account. For one person learning, this is not a toy: it is the same API you would point at a server later.

```python
mlflow.set_tracking_uri((PROJECT_ROOT / "mlruns").as_uri())
mlflow.set_experiment("raviride-eta")

with mlflow.start_run(run_name="rf_full"):
    mlflow.log_params({"max_depth": 12, "feature_set": "full"})
    mlflow.set_tags({"data_hash": data_hash})
    mlflow.log_metrics({"mae": 2.777})
    mlflow.sklearn.log_model(model, artifact_path="model")
```

Trade-offs of the local store, stated honestly:

| Choice | Good | Bad |
|---|---|---|
| File store (`mlruns/`) | Zero setup, portable, works offline | Model registry unavailable; not suitable for a team |
| SQLite backend | Registry works; still one file | Concurrent writers contend; not for a team |
| Server + database | Team access, registry, auth | Infrastructure to run and secure (Module 09) |

## 3. Comparing runs properly

The useful comparison is a table, sorted by the metric that matters, with the columns that could change the decision:

```python
runs = mlflow.search_runs(experiment_names=["raviride-eta"], order_by=["metrics.mae ASC"])
```

Sorted by aggregate MAE alone, the deepest model wins. Add `mae_peak`, `mae_zone_Z08`, and `p95_abs_error`, and the decision becomes a discussion about *where* the model is wrong - which is the discussion you want.

Two comparison habits:

- **Compare like with like.** Runs on different data or different test windows are not comparable, even if the metric name matches. That is why the dataset hash is a tag on every run.
- **Record the baseline in the same experiment.** A baseline in a slide deck drifts; a baseline run with a hash does not.

## 4. Metric choice is a product decision

For an ETA product:

| Metric | What it measures | When it is the right choice |
|---|---|---|
| MAE | Average absolute error, in minutes | Errors are equally bad and the typical case dominates |
| RMSE | Squares errors, penalising large ones | Large errors are disproportionately costly |
| p95 absolute error | The tail: 1 trip in 20 is worse than this | The product breaks on outliers (missed flights, angry riders) |
| Bias (mean signed error) | Systematic over- or under-estimation | Riders react differently to early versus late |

On this dataset, overall MAE is 2.777 minutes while p95 absolute error is 8.977. Both are true; they describe different riders. A model that improves MAE and worsens p95 has made the average better and the worst cases worse, and whether that is acceptable is a product question, not a statistical one.

## 5. Slices: where aggregates hide the truth

A **slice** is a subgroup with its own metric. Choose slices for one of three reasons:

1. **The product treats them differently** (peak versus off-peak).
2. **The data is sparse there**, so the model may be weak (peripheral zones).
3. **A failure there is a fairness or safety issue** (a zone with no service).

Measured on the course dataset with the reference model:

| Slice | Rows (test) | MAE (min) |
|---|---|---|
| All | 304 | 2.777 |
| Off-peak | 239 | 2.370 |
| Peak | 65 | 4.283 |
| Zone Z08 | 17 | 7.420 |

The aggregate is not wrong; it is incomplete. Peak-hour error is nearly twice off-peak, and Z08 is more than twice the aggregate. With 17 rows, the Z08 number carries wide uncertainty - report the count alongside the metric, always, or a 17-row slice will be treated as a law.

## 6. Baseline, and what it protects you from

A **baseline** is the result a new candidate must beat. Record it as a run and as a file (`baseline.json`), so a regression gate (Module 07) can compare against it mechanically.

Two baselines worth having:

- **Trivial**: predict the median duration. On this data that is roughly 20 minutes; any model that cannot beat it has a pipeline bug, not a modelling problem.
- **Simple**: linear regression on distance and passengers. This is the "did the complexity buy anything?" line.

## 7. Overfitting the evaluation set

Every time you compare runs on the same test rows and choose the winner, you leak a little information from the test set into your decision. Do it fifty times and the winner's score is optimistic.

Three defences, all cheap:

1. **Fix the selection rule before looking**: "lowest peak-hour MAE, provided overall MAE is within 5% of the best".
2. **Hold out a final set** you touch once, at the end (Module 09's promotion step uses this).
3. **Report the number of comparisons**: "chosen from six runs on 304 test rows" is a caveat a reader can weigh.

A model selected because it won on one evaluation is a hypothesis, not a result. Saying so is part of the evaluation report.

## 8. What tracking does not do

MLflow records what happened. It does not tell you whether the experiment was well designed, whether the slices are the right ones, or whether the model should exist. Those remain judgement, and the evaluation report is where you show your working.

# Worked example · Six runs, and the one number that is not enough

The reference project trains six variants against the same train/test split and records each one. The outputs below are from those runs; the interpretation is the part to learn.

## The experiment loop

```python
VARIANTS = [
    ("rf_basic",       "basic",    200, 12, 3),
    ("rf_calendar",    "calendar", 200, 12, 3),
    ("rf_full",        "full",     200, 12, 3),
    ("rf_full_deep",   "full",     200, 20, 1),
    ("rf_full_shallow","full",     200,  4, 3),
    ("rf_full_small",  "full",     100, 12, 3),
]

for name, feature_set, trees, depth, leaf in VARIANTS:
    with mlflow.start_run(run_name=name):
        mlflow.log_params({...})
        mlflow.set_tags({"data_hash": data_hash, ...})
        model = train_model(train_frame, params, feature_set)
        metrics = evaluate_model(model, test_frame, feature_set)
        mlflow.log_metrics({...})
        mlflow.sklearn.log_model(model, artifact_path="model")
```

On the first run in a fresh directory, MLflow reports:

```text
INFO mlflow.tracking.fluent: Experiment with name 'raviride-eta' does not exist. Creating a new experiment.
```

That message is not an error; it is the store creating its namespace. Later runs append to it.

## The comparison

```python
runs = mlflow.search_runs(experiment_names=["raviride-eta"], order_by=["metrics.mae ASC"])
cols = ["tags.mlflow.runName", "params.feature_set", "params.max_depth",
        "metrics.mae", "metrics.rmse", "metrics.p95_abs_error", "metrics.mae_peak"]
print(runs[cols].rename(columns=lambda c: c.split(".")[-1]).to_string(index=False))
```

```text
        runName feature_set  max_depth   mae   rmse   p95_abs_error  mae_peak
   rf_full_deep        full         20 2.661  5.002           8.603     4.118
        rf_full        full         12 2.777  5.259           8.977     4.283
  rf_full_small        full         12 2.810  5.343           9.238     4.362
rf_full_shallow        full          4 3.765  6.150          10.578     5.157
    rf_calendar    calendar         12 4.243  7.589          11.432     5.579
       rf_basic       basic         12 4.769  7.977          16.357     6.912
```

Read it in layers, not just down the first numeric column:

1. **Feature set is the dominant factor.** `basic` → `calendar` → `full` moves MAE from 4.769 to 4.243 to 2.777. Model size moves it far less: 20 → 4 depth moves 2.661 → 3.765, but 20 → 12 depth moves only 0.116. If you have one week to spend, spend it on features.
2. **The tail improves with the same choices, not separately.** `rf_basic`'s p95 is 16.357 minutes; `rf_full_deep`'s is 8.603. The variant that is best on average is also best in the tail, which makes the decision easier than it often is.
3. **Diminishing returns.** `rf_full_small` (100 trees) is within 0.15 minutes of `rf_full` (200 trees). At serving time, half the trees may be worth the tiny loss; that trade belongs in the report, not in a footnote.

## Where the winner is weak

Aggregate numbers hide the interesting part. Per-zone MAE for the two leading runs:

| Zone | rf_full | rf_full_deep | Test rows |
|---|---|---|---|
| Z01 | 2.59 | **2.55** | 50 |
| Z02 | 3.37 | **3.21** | 65 |
| Z03 | 1.25 | **1.22** | 45 |
| Z04 | 2.34 | **2.31** | 29 |
| Z05 | **2.39** | 2.42 | 33 |
| Z06 | 2.30 | 2.30 | 36 |
| Z07 | 2.89 | **2.67** | 29 |
| Z08 | 7.42 | **6.52** | 17 |

Three findings, in order of importance to the product:

1. **Z08 is the problem, not the model choice.** 6.52–7.42 minutes against an aggregate of 2.66–2.78. With 17 test rows the estimate is uncertain, but the direction is consistent across both models, so it is unlikely to be noise. A rider in the outer ring gets an estimate that is wrong by roughly a third of the trip.
2. **The deeper model is better in seven zones and slightly worse in one** (Z05: 2.42 versus 2.39, a difference of 0.03 minutes). That is within noise for 33 rows; do not build a story on it.
3. **Peak error is the second problem.** 4.12 minutes at peak versus roughly 2.3 off-peak. If the product promises "arriving in 6 minutes" at 18:00, that promise is the least reliable one it makes.

## The decision, written as a reviewer would need it

> Recommend `rf_full_deep` as the next baseline. It is best on MAE (2.661), RMSE (5.002), p95 (8.603), and peak-hour MAE (4.118), and better in seven of eight zones. It is marginally worse in Z05 (2.42 versus 2.39 on 33 rows), which is within sampling noise and does not change the recommendation.
>
> Two caveats. First, Z08 remains at 6.52 minutes regardless of variant; the next work should investigate that zone's data before tuning further, because no amount of depth closes a 4-minute gap that the other seven zones do not have. Second, the selection used 304 test rows and six comparisons; a final held-out evaluation is required before release (Module 09).
>
> Cost: the deeper model has more trees at greater depth, so inference is slower; measure latency before choosing it for serving (Module 10).

That is the shape of a good selection note: a recommendation, the evidence, the caveats with numbers, and the next question. It is also short enough that someone will read it.

## What the tracker made possible

Without run records, the comparison would be six terminal windows and a memory of which was which. With them, the table can be regenerated at any time, each row is tied to the dataset hash it used, and the model artefact is retrievable. That is the difference between an anecdote and evidence - and it is the only reason the paragraph above can be checked.

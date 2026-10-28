# Concepts · Module 07

## 1. Five layers, five different questions

| Layer | Question | Runs against | Speed | Cannot catch |
|---|---|---|---|---|
| Unit | Does this function compute what I think? | Fixed values, in memory | ms | Anything about data or model meaning |
| Data | Does this batch satisfy the contract? | A fixture or a batch | ms | Whether the values mean the right thing |
| Model behaviour | Does the model behave sensibly? | A fitted model | ms–s | Whether it is accurate on tomorrow's traffic |
| Integration | Do the stages work together? | The pipeline | s–min | Statistical quality |
| Regression gate | Did the metric degrade? | Recorded metrics | ms | A change that keeps MAE and breaks a slice |

The table's last column is the important one. Every layer is blind to something; a suite is credible only when it says what it does not cover.

A note on the "test pyramid": the classic advice is many unit tests, fewer integration tests. In ML the shape is flatter, because data and model tests catch failures that unit tests structurally cannot see. Do not copy the web-service shape without thinking.

## 2. Unit tests for features

Features are pure functions, which makes them the cheapest thing to test well.

```python
def test_calendar_features_are_derived_from_the_timestamp():
    frame = pd.DataFrame({"requested_at": ["2026-09-05 08:30:00"], "distance_km": [10.0]})
    out = add_features(frame)
    assert out.loc[0, "hour"] == 8
    assert out.loc[0, "day_of_week"] == 5   # Saturday
    assert out.loc[0, "is_weekend"] == 1
    assert out.loc[0, "is_peak"] == 1
```

Three properties make this a good test:

- **Exact expectations**, not `assert out["hour"] >= 0`. A test that passes for any value proves nothing.
- **A timestamp whose weekday you know**, so the assertion is checkable by hand.
- **No fixtures on disk**, so it runs in a millisecond and never fails because a data file moved.

Edge cases belong here too: zero distance (does the log produce `-inf`?), a single passenger, a missing value, the exact boundary of a range.

## 3. Data tests: fixtures, not production data

A data test asserts the contract from Module 04, using a small fixture you control.

```python
def test_duplicate_trip_ids_are_rejected(trips):
    trips.loc[1, "trip_id"] = trips.loc[0, "trip_id"]
    report = validate_trips(trips)
    assert not report.ok
    assert any(f.startswith("trip_id_unique") for f in report.failures)
```

Why a fixture: a test that depends on `data/raw/trips.csv` fails when the data changes, which is not a code regression. Worse, it passes when the file is valid for the wrong reason. The fixture makes the defect explicit, so the test proves the *check* works, not that today's batch is clean.

Parametrise to cover each rule in one place:

```python
@pytest.mark.parametrize("column,value,expected", [
    ("distance_km", -3.5, "distance_km_range"),
    ("pickup_zone", "Z99", "pickup_zone_known"),
    ("duration_min", 0.0, "duration_min_range"),
])
def test_each_defect_is_named(trips, column, value, expected):
    trips.loc[2, column] = value
    failures = validate_trips(trips).failures
    assert any(f.startswith(expected) for f in failures)
```

## 4. Behavioural tests: meaning over shape

A **behavioural test** asserts a property of the model's output that must hold regardless of the exact numbers.

| Type | Statement | Catches |
|---|---|---|
| Invariance | "The prediction must not change when X changes, but X is irrelevant" | Row-order dependence, index misalignment, accidental leakage from a column |
| Directional | "A longer trip must not be predicted faster" | Sign errors, feature inversion, a corrupted unit |
| Minimum performance | "MAE must be below this threshold on this fixture" | A model that trained on nothing, or on the wrong column |
| Consistency | "Batch and single-row prediction agree" | Training/serving skew |

The invariance test that matters most here:

```python
def test_predictions_do_not_depend_on_row_order(trained):
    model, test = trained
    x_test, _ = split_xy(test, "full")
    straight = model.predict(x_test)
    order = np.array([4, 0, 5, 2, 1, 3])
    shuffled = model.predict(x_test.iloc[order])
    assert np.allclose(shuffled, straight[order])
```

It passes on any model that treats rows independently, and fails on one that accidentally uses a fitted statistic from the batch it is predicting.

## 5. The regression gate

A gate converts a metric into a pass/fail rule:

```python
baseline = json.loads(BASELINE_PATH.read_text())["overall"]["mae"]
current = json.loads(METRICS_PATH.read_text())["overall"]["mae"]
allowed = baseline * (1 + TOLERANCE)      # TOLERANCE = 0.05
assert current <= allowed, f"MAE {current:.3f} > {allowed:.3f}"
```

Two design decisions, both consequential:

- **Tolerance.** Too tight and every legitimate change fails (retraining with a new week of data moves MAE by more than 0.1%). Too loose and real regressions pass. Five percent is a starting point, not a law; calibrate it against observed variation between acceptable runs.
- **What is baselined.** The gate compares against a *recorded accepted run*, not against the previous run. Otherwise a slow degradation passes one small step at a time.

Measured in the reference implementation: baseline MAE 2.777, allowed 2.916, degraded model 5.048 → the gate fails with a message naming all three numbers. That message is the artefact; "tests failed" is not.

## 6. Coverage, read correctly

The reference suite reports:

```text
Name                            Stmts   Miss  Cover
src\raviride_eta\data.py           82     12    85%
src\raviride_eta\features.py       30      1    97%
src\raviride_eta\prepare.py        29     29     0%
src\raviride_eta\evaluate.py       47     47     0%
TOTAL                             264    123    53%
```

Two lessons:

1. **0% on `prepare.py` and `evaluate.py` is honest, not alarming.** They are stage entry points: their logic lives in functions that *are* tested (`validate_trips`, `add_features`, `train_model`, `evaluate_model`). Coverage of a `main()` that wires modules together proves little.
2. **Coverage counts lines, not assertions.** A line executed by a test that asserts nothing is covered. The question is not "was this line run?" but "would a bug on this line fail a test?".

A useful rule: aim to cover the *logic* modules at 80%+, and do not chase the last 20% in glue.

## 7. Tests that prove nothing

The four common ways a test is worse than no test:

- **Shape-only assertions.** `assert predictions.shape == (n,)` passes for zeros.
- **Assertions on mocks.** Mocking the thing under test and asserting the mock was called.
- **A test that skips silently.** `pytest.skip` on a missing file hides a broken environment for months.
- **A test that depends on ordering or time.** Passes alone, fails in the suite; teaches people to rerun rather than investigate.

The check for all four: break the behaviour deliberately and confirm the test fails. If it does not, delete or fix it - a passing test that cannot fail is a false assurance.

## 8. What this suite still cannot do

- It cannot tell you the model will be good next month (Module 14).
- It cannot tell you the *data* is representative (Module 06's slices, plus monitoring).
- It cannot replace the evaluation report's judgement about whether the model should ship.

Tests protect behaviour you have already decided is correct. Deciding is still your job.

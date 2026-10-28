# Worked example · The bug that survived 24 tests

This example introduces a real defect into the reference project and shows, with actual output, which tests caught it. The result is uncomfortable and worth internalising.

## The defect

Someone "fixes" the distance feature by converting kilometres to miles:

```python
out["log_distance"] = np.log(out["distance_km"].clip(lower=0.1) * 0.621)
```

It is a one-character kind of mistake, made in a hurry, and the code still runs.

## What the suite said

```text
FAILED tests/test_features.py::test_log_distance_matches_natural_log - assert...
1 failed, 24 passed in 1.34s
```

The failing assertion:

```text
E         Expected: 2.302585092994046 ± 2.3e-06
```

`ln(10) = 2.302585...`; the buggy code produces `ln(6.21) = 1.826...`. Nothing else in the suite noticed.

## Why the other tests passed

| Test | Why it still passed |
|---|---|
| `test_predictions_are_positive_and_plausible` | Predictions stay in a plausible range; a monotonic transform does not change shape |
| `test_minimum_holdout_performance` | `log_distance` is redundant with `distance_km` for a tree model, so MAE barely moves |
| `test_predictions_do_not_depend_on_row_order` | Row independence is unaffected |
| `test_longer_trip_never_predicts_a_shorter_duration` | The transform is monotonic, so direction is preserved |
| Data tests | The dataset is untouched |

This is the lesson in one table. **Shape, direction, and performance tests are all blind to a monotonic transform.** They are not bad tests; they answer different questions. Only a test with a hand-computed expected value pins the definition.

The corollary matters more than the example: for every transformation, ask "which test would fail if someone changed the *formula* rather than the code structure?" If the answer is none, you have a gap.

## The fix, and the test that keeps it fixed

```python
def test_log_distance_matches_natural_log():
    frame = pd.DataFrame({"requested_at": ["2026-09-02 13:00:00"], "distance_km": [10.0]})
    out = add_features(frame)
    assert out.loc[0, "log_distance"] == pytest.approx(math.log(10.0))
```

`pytest.approx` compares floats with a tolerance, so the test is stable across platforms without being vacuous.

## The gate, with real numbers

The regression gate compares the current metrics file with a recorded baseline:

```python
TOLERANCE = 0.05
baseline = json.loads(BASELINE_PATH.read_text())["overall"]["mae"]
current  = json.loads(METRICS_PATH.read_text())["overall"]["mae"]
assert current <= baseline * (1 + TOLERANCE)
```

With a baseline of **2.777** minutes, the allowed ceiling is **2.916**. Training a deliberately weak model (`n_estimators=10`, `max_depth=2`) produced **5.048**, and the gate failed:

```text
E       AssertionError: regression: MAE 5.048 min exceeds 2.916 min
        (baseline 2.777 min, tolerance 5%)
E       assert 5.048 <= 2.9158500000000003
```

Three numbers in one message: what happened, what was allowed, what was expected. A reader can act on that without opening a notebook.

Note what the gate did *not* do: it did not compare against the previous run. Comparing run-to-run would have passed a sequence of small degradations, each within tolerance.

## The healthy run

```text
.........................                                                [100%]
25 passed in 1.26s
```

25 tests, about a second, no data files, no network. That speed is why the suite can run on every commit (Module 12).

## Coverage, and what it hid

```text
Name                            Stmts   Miss  Cover
src\raviride_eta\data.py           82     12    85%
src\raviride_eta\features.py       30      1    97%
src\raviride_eta\train.py          36     10    72%
src\raviride_eta\prepare.py        29     29     0%
src\raviride_eta\evaluate.py       47     47     0%
TOTAL                             264    123    53%
```

The bug lived in the 97%-covered `features.py`. Coverage would never have found it, because the line *was* executed - by tests that asserted nothing about its value. That is the difference between coverage and confidence, and the reason to write the assertion before looking at the percentage.

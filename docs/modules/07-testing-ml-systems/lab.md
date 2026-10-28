# Guided lab · Four layers, one gate, twenty-five tests

**Time:** 6 hours. **Tools:** Python 3.11/3.12, pytest, pytest-cov, scikit-learn. CPU only, no network.

## Scenario and business problem

The ETA pipeline now reruns quickly and records its experiments, but every change is still verified by a human comparing two MAE values. Last month a feature was silently rescaled and the team shipped it because "the metric looked fine".

You will build the safety net: tests that fail for the right reason, fast enough to run before every commit, plus a gate that refuses a model whose error has degraded beyond a stated tolerance.

### Skills practised

- Writing unit tests with exact, hand-checkable expectations.
- Parametrising data-contract tests over fixtures.
- Writing invariance, directional, and minimum-performance model tests.
- Setting and calibrating a regression gate.
- Reading coverage as a map of untested logic, not a score.

### Prerequisites

Modules 02–06. A working pipeline, a fitted model, and `metrics.json`.

### Input data

A **fixture**, built in the test code, not `data/raw/`. The fixture must contain valid rows and enough variety (zones, hours, distances) for a model to learn something. Optionally, keep `data/raw/trips_bad.csv` for one integration test.

### Directory layout

```text
raviride-eta/
├── tests/
│   ├── conftest.py
│   ├── test_features.py
│   ├── test_data.py
│   ├── test_model.py
│   └── test_regression_gate.py
├── baseline.json
└── docs/test-strategy.md
```

## Part 1: the fixture (30 minutes)

1. In `conftest.py`, write `make_trips(rows=24)` producing a deterministic DataFrame with all eleven columns. Derive `duration_min` from distance, zone pace, peak status, and passengers so the data has learnable structure.
2. Expose three fixtures: `trips` (a fresh frame per test), `trips_factory` (the function), and `featured` (the frame after `add_features`).
   **Checkpoint 1:** `pytest --fixtures` lists them, and no fixture reads a file.

*Why build rather than load:* a test that reads `data/raw/trips.csv` fails when the data is regenerated, which is not a code defect, and passes when the file is valid for reasons unrelated to the check.

## Part 2: unit tests for features (45 minutes)

3. Write at least five tests in `test_features.py`:
   - calendar fields from a known Saturday timestamp (assert hour, day-of-week, weekend, peak);
   - off-peak weekday not flagged;
   - `log_distance == ln(distance)`, using `pytest.approx`;
   - zero distance does not produce `-inf`;
   - no feature set contains `fare_amount` (parametrised over all sets);
   - unknown feature set raises `ValueError`.
   **Checkpoint 2:** change `log_distance` to use miles (multiply by 0.621) and confirm exactly one test fails. Restore it.

## Part 3: data tests (45 minutes)

4. Write one test per check in `test_data.py`, each mutating a single value:
   duplicate id, negative distance, retired zone, timestamp outside window, implausible speed, missing column.
5. Add a test that the raised exception message names the file, the rule, and a row.
   **Checkpoint 3:** all data tests pass, and each one fails if you delete its check from `validate_trips`.

## Part 4: behavioural tests (75 minutes)

6. In `test_model.py`, train a small model inside a fixture: 18 rows train, 6 hold out, `n_estimators=60`, `random_state=42`.
7. Write:
   - predictions positive and below 240 minutes;
   - holdout MAE below a calibrated threshold (start at 3.5; record the measured value in a comment);
   - row-order invariance;
   - extra irrelevant column ignored;
   - longer distance never predicts a shorter duration;
   - peak not predicted faster than off-peak, with a small tolerance.
   **Checkpoint 4:** all six pass, and the suite still runs in under three seconds.

*Recovery:* if row-order invariance fails, you are indexing the frame by position somewhere; use `.iloc` consistently and compare predictions against the permuted truth.

## Part 5: the gate (45 minutes)

8. Record a baseline from an accepted run:
   ```powershell
   Copy-Item metrics.json baseline.json
   ```
9. Write `test_regression_gate.py` with a 5% tolerance and a clear failure message. Skip cleanly when either file is missing.
10. Prove the gate works:
    ```powershell
    # degrade the model deliberately
    python -m raviride_eta.train
    python -m raviride_eta.evaluate
    python -m pytest tests/test_regression_gate.py
    ```
    **Checkpoint 5:** the test fails, naming current, allowed, and baseline MAE. Restore the parameters, rerun, and the test passes.

## Part 6: coverage and the strategy note (60 minutes)

11. Run:
    ```powershell
    python -m pytest --cov=raviride_eta --cov-report=term-missing
    ```
12. **Checkpoint 6:** record the total percentage and the two lowest modules in `docs/test-strategy.md`.
13. Explain why the 0% modules are acceptable (or not), in two sentences each.
14. Write the strategy note: the risk → test → what-it-cannot-catch table for this project, and the three things the suite does not protect against.
15. Commit. The suite must run with no arguments from the repository root.

## Expected outputs

| Output | Reference values |
|---|---|
| Tests | 25 passing, ~1.3 s |
| Coverage | 53% total; `features.py` 97%, `data.py` 85%, stage mains 0% |
| Gate failure | `MAE 5.048 min exceeds 2.916 min (baseline 2.777 min, tolerance 5%)` |
| Gate pass | after restoring parameters, 2.777 |
| Unit-bug demo | 1 failed, 24 passed |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Meaningfulness | Each test fails when its behaviour is broken; you demonstrated at least two |
| Independence | Tests pass in any order and individually (`pytest tests/test_model.py`) |
| Speed | Full suite under five seconds, no network, no live data dependency |
| Gate | Fails on the degraded model, passes on the accepted one, and explains why |
| Honesty | The strategy note names what is not covered, including slices and drift |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `fixture 'trips' not found` | `conftest.py` not in a parent directory of the test | Move it to `tests/` root |
| Model test slow | Refitting a large forest per test | Reduce trees, cache within a module-scoped fixture if the frame is immutable |
| Invariance test fails | Positional index used after permutation | Use `.iloc` and compare against permuted predictions |
| Gate skips unexpectedly | `baseline.json` missing or written elsewhere | Check paths are derived from `PROJECT_ROOT` |
| Different MAE from the lab | Fixture differs | Compare row counts and feature list before changing the threshold |
| `pytest` picks up notebooks | Test discovery too broad | Set `testpaths = ["tests"]` in `pyproject.toml` |

## Cleanup

- Restore `params.yaml` and regenerate the good model: `dvc repro`.
- Keep `baseline.json`; it is the gate's reference.
- No services were started.

## Optional extensions

1. **Property-based tests.** Install `hypothesis`, generate distances and passengers, and assert invariants (prediction finite, positive, monotone in distance). Record one case it finds that your example-based tests missed.
2. **Slice gate.** Extend the gate to fail when Z08's MAE degrades by more than 15%, and explain why a single aggregate tolerance is insufficient for this product.
3. **Mutation check.** Break one line of `features.py` at a time and count how many tests fail for each mutation. Report the mutation score and which functions are weakly tested.

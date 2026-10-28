# Lab 07 · Write the tests that catch leakage

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L07 | Intermediate | 4 hours | [07 · Testing ML systems](../modules/07-testing-ml-systems/index.md), [04 · Data quality](../modules/04-data-quality-versioning/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-07-leakage-tests/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-07-leakage-tests) — starter files, data generator, and acceptance checker.

## Scenario

The session-score model reports an MAE of 3.0, which is 33% better than the same
model before last week's "improvements". The improvements were: adding
`score_band` as a feature, switching to a random row-level split, and fitting the
imputer on the whole dataset before splitting. All three are leakage, and all
three make the number better.

The model is not better. Your job is to write tests that prove it — tests that
fail on this pipeline and pass once it is fixed. A test that fails on both is a
broken test, not a leak detector.

## What you will be able to do

- Distinguish target leakage, group leakage and preprocessing leakage.
- Write a test for each that fails for the right reason.
- Design a test suite that is sensitive to the defect and quiet on correct code.
- Explain why a suspiciously good metric is a warning, not a result.

## Prerequisites and setup

```bash
cd examples/labs/lab-07-leakage-tests
python make_data.py
python -c "import leaky_pipeline as p; print(p.run()['mae'])"
```

Expected: 318 sessions from 90 students, 11 missing prior scores, and a leaky MAE
around `3.0044`. Every student appears in both splits, and the imputer sees all
318 rows.

## Your task

Implement the three failing tests in `tests/test_leakage.py`, then replace the
re-export in `pipeline.py` with a corrected `run()` that keeps the same return
contract. `check_lab07.py` runs your suite twice.

## Data and starter files

| File | Purpose |
|---|---|
| `make_data.py` | 318 sessions, 90 students, 4% missing prior scores |
| `leaky_pipeline.py` | Frozen production pipeline (do not edit) |
| `pipeline.py` | Starts as `from leaky_pipeline import run`; yours to rewrite |
| `tests/test_leakage.py` | Two passing tests, three that raise `AssertionError` |
| `check_lab07.py` | Red run against the leaky module, green run against yours |

`run()` returns `mae`, `features`, `train_groups`, `test_groups`, `rows_train`,
`rows_test`, `imputer_fit_rows`.

## Steps

### 1. Confirm the three leaks

Run the leaky pipeline and inspect its return value:

```bash
python -c "import leaky_pipeline as p; r=p.run(); print(r['features']); print(len(set(r['train_groups']) & set(r['test_groups']))); print(r['imputer_fit_rows'], r['rows_train'])"
```

Expected: `['hours', 'prior_score', 'sleep_hours', 'score_band']`, an overlap of
51 students, and `318 238`.

### 2. Write the target-leak test

Assert that no feature is derived from the target. Be specific about what you
consider target-derived (`score*` except `prior_score`), and make the failure
message name the offending column.

### 3. Write the group test

Assert that the intersection of `train_groups` and `test_groups` is empty.

### 4. Write the preprocessing test

Assert `imputer_fit_rows == rows_train`. A model must not learn a mean from rows
it will be evaluated on.

### 5. Fix the pipeline

Remove `score_band`, split by `student_id` with `GroupShuffleSplit`, fit the
imputer on training rows only. Keep the return contract, or the tests cannot run.

### 6. Run both directions

```bash
LAB07_PIPELINE=leaky_pipeline python -m pytest tests -q
python -m pytest tests -q
```

```powershell
$env:LAB07_PIPELINE="leaky_pipeline"; python -m pytest tests -q; Remove-Item Env:\LAB07_PIPELINE
python -m pytest tests -q
```

Expected: three failures, then four passes. The fixed MAE is about `4.4651` —
worse than the leaky number, and honest.

### 7. Run the checker

```bash
python check_lab07.py
```

Expected: `6/6 checks passed`.

## Expected output

```text
  [PASS] suite fails against the leaky pipeline -- exit 1
  [PASS] catches imputer_is_fitted_on_training_rows_only -- failed: [...]
  [PASS] catches no_target_derived_feature -- failed: [...]
  [PASS] catches students_do_not_cross_the_split -- failed: [...]
  [PASS] suite passes against the fixed pipeline -- 4 passed in 1.36s
  [PASS] no unrelated tests fail on the leaky pipeline -- clean
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Suite fails on the leaky pipeline | Exit 1 |
| 2 | `test_no_target_derived_feature` fails there | Named in the failure list |
| 3 | `test_students_do_not_cross_the_split` fails there | Named |
| 4 | `test_imputer_is_fitted_on_training_rows_only` fails there | Named |
| 5 | Suite passes on the fixed pipeline | Exit 0 |
| 6 | No unrelated test fails on the leaky pipeline | Clean |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| All tests fail on both pipelines | Tests import a stale module or the contract changed | Keep the return keys; run with `python -m pytest` from the lab root |
| A leak test passes on the leaky pipeline | Assertion is too weak (e.g. checks for `score` only) | Match `score_band` explicitly or use a `score*` prefix |
| Group test errors on missing keys | Student removed `train_groups` from the return value | Keep the contract; it is what makes the test possible |
| MAE equals the leaky number after the fix | `pipeline.py` still re-exports `leaky_pipeline` | Write your own `run` |
| Fixed pipeline fails the group test | `train_test_split` still used | Use `GroupShuffleSplit(groups=...)` |

## Reflection questions

1. Which of the three defects would a reviewer spot from the code, and which
   only from the metric's magnitude?
2. Why is the fixed model's worse MAE the correct outcome?
3. What would a leakage test look like for a time-series problem, where groups
   are dates rather than students?
4. Your test suite now encodes the contract. What happens to it when a future
   model legitimately needs a target-derived feature during training only?

## Optional extension

Add a fourth test for temporal leakage: construct a dataset with a date column and
assert that the latest training date precedes the earliest test date. Then explain
in three sentences why random splitting is invalid for that data.

## Cleanup

```bash
rm -rf data .pytest_cache __pycache__
```

PowerShell: `Remove-Item data, .pytest_cache, __pycache__ -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I reproduced the three leaks from the pipeline's own return values
- [ ] Each of my three tests fails on the leaky pipeline for the right reason
- [ ] The fixed pipeline passes all tests
- [ ] I can explain why the honest MAE is higher
- [ ] `check_lab07.py` reports `ACCEPTED`

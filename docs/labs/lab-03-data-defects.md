# Lab 03 · Find every defect in a supplier drop

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L03 | Intermediate | 3 hours | [04 · Data quality and versioning](../modules/04-data-quality-versioning/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-03-data-defects/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-03-data-defects) — starter files, data generator, and acceptance checker.

## Scenario

A student-information system sends a nightly CSV export. On Tuesday it is clean.
On Wednesday four things are wrong with it. On Thursday the upstream team
renames a column without telling anyone, and the loader reports the failure as
`KeyError: 'prior_score'` in a line of code nobody recognises.

Your validator must reject both bad drops with a complete report in one pass, and
accept the clean one. A validator that stops at the first defect forces the
upstream team to fix issues one at a time, one day per issue.

## What you will be able to do

- Turn a data expectation into a check with a stable failure code and a count.
- Write a validator that reports all defects, not the first one.
- Handle a schema change as a distinct class of failure.
- Prove the validator accepts good data, which is the half everyone skips.

## Prerequisites and setup

```bash
cd examples/labs/lab-03-data-defects
python make_batches.py
python validate.py data/clean_batch.csv
python validate.py data/bad_batch.csv
```

The generator writes three 180-row files into `data/`:

| File | Planted defects |
|---|---|
| `clean_batch.csv` | none |
| `bad_batch.csv` | 6 missing sleep values, 3 impossible study durations, 4 duplicated ids, 2 unknown sections |
| `schema_change.csv` | `prior_score` renamed to `prior_grade`, extra `cohort` column |

## Your task

Complete `validate.py` so that it implements six checks and keeps the report
contract. Run `python check_lab03.py` when you think you are done.

The contract:

```json
{"path": "data/bad_batch.csv", "rows": 180, "ok": false,
 "checks_run": ["schema", "duplicate_ids", "missing_values", "hours_range", "score_range", "unknown_section"],
 "failures": [{"code": "missing_values", "count": 6, "example": "sleep_hours"}]}
```

Exit code 0 for accepted, 1 for rejected. A schema failure stops column checks
(they cannot run) but must still write the report.

## Data and starter files

| File | Purpose |
|---|---|
| `make_batches.py` | Deterministic generator for the three drops |
| `validate.py` | Partially implemented validator: schema and duplicates only |
| `check_lab03.py` | Acceptance checker with the planted counts |

## Steps

### 1. Confirm what the starter catches

```bash
python validate.py data/bad_batch.csv
```

Expected:

```text
FAIL data/bad_batch.csv: 180 rows, 2 checks
  - duplicate_ids: 4 (S0011)
```

Four defects is one line of output. That gap is the lab.

### 2. Add the missing-value check

Count rows where any of `hours`, `prior_score`, `sleep_hours`, `score` is null,
not null cells. The count is the number of affected rows; the example names the
columns involved. Expected count on the bad batch: **6**.

### 3. Add range checks

- `hours` within `[0.25, 16]` — three violations are planted.
- `prior_score` and `score` within `[0, 100]`.

Do not let nulls appear as range violations as well; a missing value is one
defect, reported once.

### 4. Add the category check

`section` must be one of `A`, `B`, `C`. Two rows use `D`.

### 5. Handle the schema change

Do not crash on a missing column. Report `schema_missing` with the column names
and `schema_extra` for columns that are not expected. A rename necessarily
produces both: one missing, one extra. That is the honest report — the validator
cannot know the two are related.

### 6. Prove the good batch passes

```bash
python validate.py data/clean_batch.csv
```

Must exit 0 with no failures. A validator that rejects everything passes half
the tests and fails the production rollout.

### 7. Run the checker

```bash
python check_lab03.py
```

Expected: `17/17 checks passed`.

## Expected output

Reference solution on the bad batch:

```text
FAIL data/bad_batch.csv: 180 rows, 6 checks
  - duplicate_ids: 4 (S0011)
  - missing_values: 6 (sleep_hours)
  - hours_range: 3 (S0008 hours=31.2)
  - unknown_section: 2 (S0023 section=D)
```

On the schema change:

```text
FAIL data/schema_change.csv: 180 rows, 1 checks
  - schema_missing: 1 (prior_score)
  - schema_extra: 2 (prior_grade, cohort)
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Bad batch exit code | 1 |
| 2 | `missing_values` count | 6 |
| 3 | `hours_range` count | 3 |
| 4 | `duplicate_ids` count | 4 |
| 5 | `unknown_section` count | 2 |
| 6 | Schema change reports missing and extra | 1 and 2 |
| 7 | Clean batch exits 0 with no failures | Yes |
| 8 | Report written to `--json` path | Yes, with `checks_run` listing every check that ran |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `hours_range` count is 6 | Nulls compare as out-of-range | Exclude nulls from range checks |
| Schema file crashes with `KeyError` | Column checks run before the schema check | Return early after reporting missing columns |
| Clean batch fails `score_range` | Inclusive bounds written as exclusive | Use `between(0, 100)` |
| `missing_values` counts cells, not rows | `frame.isna().sum().sum()` | Use `frame[cols].isna().any(axis=1).sum()` |
| JSON report has tuples | `json.dumps` on numpy types | Cast counts to `int` |

## Reflection questions

1. Why report a renamed column as two defects instead of guessing the mapping?
2. Which of the six checks would have caught the incident in the scenario, and
   which would have caught it *before* training started?
3. Is `hours > 16` a data error or a legitimate long session? Who decides, and
   where should that decision live?
4. What would you add to this report so an upstream engineer can fix the file
   without asking you a question?

## Optional extension

Add a `--strict` mode that treats `schema_extra` as a warning instead of a
failure, and record why a new column is sometimes harmless. Then add a test that
proves the same file produces different exit codes in the two modes.

## Cleanup

```bash
rm -rf data artifacts
```

PowerShell: `Remove-Item data, artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I saw the starter catch only 2 of 6 checks
- [ ] All four defect groups are reported in one pass
- [ ] The schema change is reported without a traceback
- [ ] The clean batch is accepted
- [ ] `check_lab03.py` reports `ACCEPTED`

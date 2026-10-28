# Lab 13 · Diagnose a dependency incompatibility

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L13 | Intermediate | 2 hours | [02 · Python, Git, environments](../modules/02-python-git-cli-environments/index.md), [11 · Docker and containers](../modules/11-docker-containers/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-13-dependency-conflict/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-13-dependency-conflict) — starter files, data generator, and acceptance checker.

## Scenario

Two services were merged into one repository. The reporting service still carries
requirements from when pandas 1.5 was current. The pipeline was written against
pandas 2.2. Both files install, one after the other, and the result imports
fine — then fails at runtime with:

```text
AttributeError: 'DataFrame' object has no attribute 'append'
```

No version number appears in that message. The stack trace points at your code,
not at the dependency, and the code was correct for the version it was written
for. This is the most common shape of "works on my machine".

## What you will be able to do

- Distinguish a missing package from a removed API.
- Find conflicting pins before installing anything, using only `packaging`.
- Fix code for the installed major version without downgrading the environment.
- Add a test that fails at the right version boundary.

## Prerequisites and setup

```bash
cd examples/labs/lab-13-dependency-conflict
python make_data.py
python resolve.py requirements.txt requirements-legacy.txt
python pipeline.py
```

Expected: two conflict lines from `resolve.py`, then the `AttributeError` from
`pipeline.py`.

## Your task

Unify the requirements so they install together, fix the pipeline for pandas 2,
and add a test that catches the same class of problem next time.

## Data and starter files

| File | Purpose |
|---|---|
| `requirements.txt` | Current application pins (pandas 2.2.3) |
| `requirements-legacy.txt` | The reporting service's old pins |
| `resolve.py` | Offline conflict checker over `packaging` |
| `pipeline.py` | Reads two extracts and concatenates them with `append` |
| `tests/test_pipeline.py` | Two passing tests, one failing |
| `check_lab13.py` | Conflict, runtime, and test checks |

## Steps

### 1. Read the conflict precisely

```bash
python resolve.py requirements.txt requirements-legacy.txt
```

```text
3 packages across 2 files
  CONFLICT pandas: pinned to 1.5.3, 2.2.3 by different files
  CONFLICT numpy: pinned to 1.26.4, 2.5.4 by different files
  CONFLICT scikit-learn: pinned to 1.2.2, 1.5.2 by different files
```

This is a *pin* conflict, not an API conflict, and it is the easy half.

### 2. Reproduce the runtime failure

```bash
python pipeline.py
```

The traceback ends in `pandas/core/generic.py`, which is a strong hint that the
API, not your logic, is missing. Confirm the installed version:

```bash
python -c "import pandas; print(pandas.__version__)"
```

### 3. Replace the removed API

`DataFrame.append` was removed in pandas 2.0. `pd.concat([a, b], axis=0,
ignore_index=True)` is the replacement. Preserve the intent: the old call
appended and reindexed; the new one should produce the same 600 rows and no
duplicates.

### 4. Unify the requirement files

Either delete the legacy pins or make the legacy file reference the project file:

```text
-r requirements.txt
```

`resolve.py` ignores `-r` lines, which is correct: the reference is resolved by
pip, not by this checker.

### 5. Add the boundary test

A test that only exercises `load()` will catch this bug today and forget it
tomorrow. Add one that fails if pandas drops below the supported major:

```python
assert Version(pd.__version__) >= Version("2.0")
```

and one that asserts the requirement file pins that major.

### 6. Run the checker

```bash
python check_lab13.py
```

Expected: `9/9 checks passed`.

## Expected output

```text
  [PASS] requirement files install together -- no conflicts: the set can be installed together
  [PASS] pandas is pinned to the major the code runs on -- pandas==2.
  [PASS] the pipeline no longer calls the removed DataFrame.append
  [PASS] the pipeline runs on the pinned environment
  [PASS] both extracts are summarised -- got 600, expected 600
  [PASS] the summary has no nulls -- {'rows': 600, 'mean_hours': 2.061, ...}
  [PASS] the test suite passes -- 5 passed in 0.37s
  [PASS] the suite has at least three tests -- 5 tests
  [PASS] the installed pandas is 2.x -- ['2.2.3', '2.5.4', '1.5.2']
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Requirement files have no conflicting pins | `resolve.py` exit 0 |
| 2 | `pipeline.py` runs | Exit 0, summary written |
| 3 | Both extracts present | 600 rows, unique ids |
| 4 | Removed API no longer called | No `append(extra` |
| 5 | Test suite passes | At least three tests |
| 6 | Version boundary is tested | Version guard present |
| 7 | pandas pinned to 2.x | Pin inspected |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `resolve.py` still reports a conflict | Legacy file edited but not saved, or a second pin elsewhere | Run it on every `requirements*.txt` |
| `ModuleNotFoundError: packaging` | Not installed | `pip install packaging` (already in the lab requirements) |
| Test passes but pipeline fails | Test imports a cached module | Restart pytest; check `sys.path` |
| `NameError: Version` | Missing import | `from packaging.version import Version` |
| Downgrading pandas seems easier | It is, briefly | The service needs 2.x; fix the code |

## Reflection questions

1. Why did pip not report this as a conflict at install time?
2. What is the difference between a pin conflict and an API incompatibility, and
   which one does `resolve.py` catch?
3. Where should the supported version range be declared so that tests, CI and the
   container all read the same answer?
4. How would a lock file have changed the diagnosis?

## Optional extension

Create a second virtual environment with pandas 1.5.3 and run the same test suite.
Record which tests fail and whether the failure message names the version. Then
explain why running the suite on two versions is worth the time in CI.

## Cleanup

```bash
rm -rf data artifacts .pytest_cache
```

PowerShell: `Remove-Item data, artifacts, .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I saw the conflict before installing anything
- [ ] I reproduced the runtime failure and identified the removed API
- [ ] The pipeline runs on pandas 2.x without downgrading
- [ ] The requirement files agree
- [ ] A test now fails if the version boundary moves
- [ ] `check_lab13.py` reports `ACCEPTED`

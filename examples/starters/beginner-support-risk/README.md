# Beginner starter — support-risk classifier

A complete, small supervised-learning project: generated data, validation, one
pipeline object, a metric floor, and tests. Copy this folder to start a project
of your own; nothing here imports the course repository.

| | |
|---|---|
| **Level** | Beginner |
| **Task** | Binary classification |
| **Data** | Synthetic, generated locally |
| **Time to run** | About one minute |
| **Needs** | Python 3.11+, no network beyond installing packages |

---

## What it demonstrates

- A **project layout** that separates data handling, model, entry point, and tests.
- **Validation with specific errors** instead of failing later inside scikit-learn.
- A **single pipeline** holding preprocessing and the estimator, so there is no
  separate prepared file to drift.
- A **metric floor** in configuration, enforced by the exit code.
- **Determinism**: same seed, same metrics, tested rather than asserted in prose.

It deliberately leaves out a registry, a service, a container, CI, and
monitoring. Those are the intermediate and advanced starters, and adding them
here would hide the structure that this level is about.

---

## Layout

```text
beginner-support-risk/
├── config.yaml              # paths, model choice, seed, metric floor
├── data/                    # generated; not committed
├── artifacts/               # generated: model, metrics, metadata
├── make_data.py             # deterministic local data generator
├── train.py                 # entry point; exits non-zero below the floor
├── requirements.txt
├── pytest.ini
├── src/support_risk/
│   ├── __init__.py
│   ├── data.py              # load, validate, split, feature_frame
│   └── model.py             # build_pipeline, evaluate, train
└── tests/
    ├── test_data.py         # nine validation and leakage tests
    └── test_model.py        # determinism, metric floor, saved artifact
```

---

## Run it

From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python make_data.py
python train.py
python -m pytest
```

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python make_data.py
python train.py
python -m pytest
```

### Expected output

```text
$ python make_data.py
wrote data/study_support.csv  300 rows  82 positive

$ python train.py
model        logistic
train rows   225
test rows    75
roc_auc      0.8977
accuracy     0.8400
recall       0.6667
artifacts    .../artifacts
PASS: roc_auc 0.8977 >= floor 0.7000

$ python -m pytest
13 passed
```

Tolerances: your ROC AUC will be within about ±0.03 if you keep the seed and the
pins. Accuracy and recall move more, because 75 test rows is a small sample — a
single row is 1.3 percentage points. Do not treat a one-point difference as a
finding.

---

## Read the code in this order

1. `make_data.py` — where the data comes from, and why the label is a function.
2. `src/support_risk/data.py` — `validate()` and `split()`.
3. `src/support_risk/model.py` — `build_pipeline()` and `train()`.
4. `train.py` — the floor check that turns a metric into an exit code.
5. `tests/test_data.py` — what each validation rule defends against.

---

## Exercises

1. **Break validation on purpose.** Set `attendance_rate` to `1.4` in one row and
   run `train.py`. You should see the range error, not a scikit-learn traceback.
   Which line catches it?
2. **Change the model** to `forest` in `config.yaml` and rerun. Record both
   metrics. Does the extra capacity help, and is the difference larger than the
   test-set noise you can estimate by changing the seed?
3. **Add a slice.** Compute ROC AUC separately for `prior_gpa_band == "low"` and
   `== "high"` in `evaluate()`. Add it to `metrics.json` under `slices`. This is
   the first step toward the evaluation discipline in Module 06.
4. **Make the floor fail.** Set `min_roc_auc: 0.99`, run `train.py`, and check the
   exit code (`echo $?` in bash, `$LASTEXITCODE` in PowerShell). A gate that
   cannot fail is decoration.
5. **Remove the identifier properly.** Add `student_ref` to `NUMERIC` and observe
   what breaks. Why is that a data-type error rather than a modelling choice?

---

## Common problems

| Symptom | Cause | Fix |
|---|---|---|
| `DataError: ... does not exist; run python make_data.py first` | Data not generated | Run `python make_data.py` |
| `ModuleNotFoundError: support_risk` | Running Python from the parent directory | `cd` into this folder; `train.py` adds `src/` to the path |
| `pytest: command not found` | Virtual environment not active | Activate it, or use `python -m pytest` |
| ROC AUC around 0.5 | `min_roc_auc` not the problem — the features are | Check that `feature_frame()` returns the numeric columns, not strings |
| PowerShell refuses to activate the venv | Execution policy | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |

---

## Cleanup

```bash
rm -rf data artifacts .pytest_cache src/support_risk/__pycache__ tests/__pycache__
```

```powershell
Remove-Item data, artifacts, .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

Keep `.venv` if you are continuing to the next starter; it has the same pins.

---

## Where this sits in the course

| Before this | This starter | Next |
|---|---|---|
| [Module 03 · Project organization](../../../docs/modules/03-project-organization/index.md) | A project a stranger can run and test | [Intermediate starter](../intermediate-eta-service/README.md) |
| [Lab 02 · Script into a project](../../../docs/labs/lab-02-refactor-notebook.md) | The same refactor, done | [Lab 07 · Leakage tests](../../../docs/labs/lab-07-leakage-tests.md) |

The data contract, the split, and the floor are the three things every later
project keeps. The modelling code is the part you are expected to replace.

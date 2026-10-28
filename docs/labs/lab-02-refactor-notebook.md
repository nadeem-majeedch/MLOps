# Lab 02 · Turn a working script into a project

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L02 | Foundation | 3 hours | [03 · Project organisation](../modules/03-project-organization/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-02-refactor-to-project/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-02-refactor-to-project) — starter files, data generator, and acceptance checker.

## Scenario

`train_all_in_one.py` trains the study-score model and prints a useful number.
It also reads the dataset when the module is imported, takes no arguments,
writes `model.pkl` into whatever directory you happen to be in, and hard-codes
the split, the seed and three feature names. It has been copied into two other
folders, and one of those copies is now the one the weekly report uses.

You are asked to make it importable, testable and callable from a scheduler,
without changing what it measures. This is refactoring, not rewriting: the last
number it prints must still be obtainable afterwards.

## What you will be able to do

- Move code into a package with a single entry point and no import-time work.
- Replace hard-coded decisions with arguments and settings.
- Separate loading, features and training so each can be tested alone.
- Add the first tests that pin behaviour rather than implementation.

## Prerequisites and setup

```bash
cd examples/labs/lab-02-refactor-to-project
python ../_shared/make_sessions.py --out data/sessions.csv
python train_all_in_one.py
```

Expected: three lines ending with `wrote model.pkl`, and a `model.pkl` in the lab
directory. Note the working directory: running it from the repository root
fails, which is the first defect to fix.

## Your task

Produce a package under `src/` with a CLI entry point, a metrics artefact, and a
test suite. `check_lab02.py` defines the contract:

```bash
python check_lab02.py --module sessionlab.train
```

## Data and starter files

| File | Purpose |
|---|---|
| `train_all_in_one.py` | The script as it exists today |
| `check_lab02.py` | Structural acceptance checker |
| `data/sessions.csv` | 480 synthetic sessions |

The checker looks for a package (`src/<name>/__init__.py`), at least two
non-package modules, an entry point that answers `--help`, a command that writes
`artifacts/run.json` with `mae`, `rows_train`, `rows_test` and `model_path`, a
passing suite under `tests/`, and no absolute Windows paths in the package.

## Steps

### 1. Write down what must not change

Before moving anything, record the current behaviour:

```bash
python train_all_in_one.py
```

Write the input, the split, the seed and the metric into a short note. This note
is your regression oracle: after the refactor, the same inputs must produce the
same number.

### 2. Create the package skeleton

```text
lab-02-refactor-to-project/
├── src/sessionlab/
│   ├── __init__.py
│   ├── config.py      settings and feature names
│   ├── data.py        loading and splitting
│   ├── features.py    pure transforms
│   └── train.py       CLI: parse, fit, report
├── tests/
│   └── test_features.py
└── artifacts/
```

Nothing may read a file at import time. A module that does I/O on import cannot
be imported by a test, a notebook or a scheduler, which is why the checker
imports your module from the parent directory and expects silence.

### 3. Move one concern at a time

Move loading first, run the script, compare the number. Then features, then
training. If the number moves, you changed behaviour rather than structure.

### 4. Add arguments and a metrics file

The command must work from any directory:

```bash
python -m sessionlab.train --data data/sessions.csv --out artifacts/run.json --seed 7
```

`PYTHONPATH=src` (or `pip install -e .`) is required until the package is
installed. The checker sets it for you.

### 5. Write tests that would fail if the transform broke

Start with a purity test (the input frame is not mutated), a value test
(`study_ratio = hours / prior_score`) and an edge case (zero prior score must not
divide by zero).

### 6. Run the checker

```bash
python check_lab02.py --module sessionlab.train
```

Expected final line: `L02 Notebook script to maintainable project: 11/11 checks passed`.

## Expected output

The reference solution produces:

```text
  [PASS] package exists under src/ -- sessionlab
  [PASS] training code split across at least two modules -- 4: ['config.py', 'data.py', 'features.py', 'train.py']
  [PASS] no module over 200 lines -- longest 57 lines
  [PASS] the training entry point answers --help -- no output
  [PASS] importing the module does no work -- exit 0, stdout ''
  [PASS] one command writes artifacts/run.json -- no stderr
  [PASS] metrics file has the agreed keys -- all present
  [PASS] mae is a finite number -- mae=4.501
  [PASS] tests/ holds at least one test file -- test_features.py
  [PASS] the test suite passes -- 4 passed in 0.48s
  [PASS] no absolute Windows paths in the package -- []
```

Your MAE depends on your split; 4.5 ± 0.4 is expected with the default seed and
a 25% test split.

## Acceptance criteria

| # | Criterion | How it is checked |
|---|---|---|
| 1 | Package under `src/` with at least two modules | Directory scan |
| 2 | `--help` works for the entry point | Subprocess, exit 0 |
| 3 | Importing the module produces no output and no I/O | Import from parent directory |
| 4 | One command writes metrics with the agreed keys | JSON parsed and keys compared |
| 5 | Tests exist and pass | `pytest` exit code |
| 6 | No absolute paths in the package | Text scan for `C:\` |
| 7 | Behaviour preserved | Your recorded number matches the new run |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: sessionlab` | `src/` not on the path | `PYTHONPATH=src` or `pip install -e .` |
| Checker reports import output or exit 1 | Module-level `read_csv` or `print` | Move work inside functions |
| `--help` prints nothing, exit 2 | `argparse` parser built but `main()` not called | Call it under `if __name__ == "__main__":` |
| Tests import the wrong copy | An old `sessionlab` installed in site-packages | Uninstall it, or run with `PYTHONPATH=src` |
| MAE moved after refactor | Seed or split changed | Pass the seed through; compare `rows_train` first |

## Reflection questions

1. Which of the four modules could be deleted without changing the output, and
   what would that cost later?
2. The original script imports and trains in one step. What specifically breaks
   when a scheduler imports it?
3. Why is a metrics JSON file more useful to a reviewer than a printed line?
4. Where should the feature list live so that training and serving cannot drift?

## Optional extension

Add a `--feature-set` option with `core` and `full` variants, and a test that
asserts the two produce different feature counts. This is the shape Module 09
uses for candidate comparison.

## Cleanup

```bash
rm -rf artifacts model.pkl data
```

PowerShell: `Remove-Item artifacts, model.pkl, data -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I recorded the original number before refactoring
- [ ] The package imports with no side effects
- [ ] One command produces a metrics file with the agreed keys
- [ ] At least three tests pass and one covers an edge case
- [ ] `check_lab02.py` reports `ACCEPTED`

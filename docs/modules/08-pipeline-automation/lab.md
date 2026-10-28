# Guided lab · One command, one failure, one recovery

**Time:** 4 hours. **Tools:** Python 3.11/3.12, DVC 3.x, Git, `pre-commit`. CPU only, no network beyond installing packages.

## Scenario and business problem

RaviRide's ETA model is retrained about twice a week. The current procedure is a page in a wiki: five commands, in order, "after activating the environment". Last Thursday the on-call engineer ran them out of order, trained on last week's features, and reported an improvement. The model was fine; the process was not.

Your job is to make the pipeline operable by someone who has never seen it: one command, declared inputs, a log, an exit code, and a rerun that behaves predictably after a failure. Acceptance is not "it runs on my machine" — it is "a colleague can predict what the second run will do".

### Skills practised

- Declaring and reading a stage graph with parameters and outputs.
- Reasoning about cache keys instead of guessing.
- Designing failures that stop the pipeline, and reading the resulting state.
- Writing a small entry point with preflight checks and exit codes.
- Adding commit-time hooks that reject the two mistakes most likely to reach review.

### Prerequisites

- Modules 02–07 complete: a package under `src/raviride_eta/`, a working `dvc repro`, and a test suite.
- `dvc` on the PATH of the environment you will use.
- A Git repository with at least one commit.

### Input data

`data/raw/trips.csv` (1,200 rows), tracked with `dvc add` in Module 04, and `data/raw/trips_bad.csv` for the failure test. Regenerate both if needed:

```powershell
python scripts/generate_trips.py --out data/raw/trips.csv
python scripts/generate_trips.py --out data/raw/trips_bad.csv --corrupt
```

Do not edit the raw CSV by hand; a hand-edited dataset is a dataset you cannot regenerate.

### Directory layout you will build

```text
raviride-eta/
├── dvc.yaml                  # the declaration
├── dvc.lock                  # the record (committed)
├── params.yaml
├── run_pipeline.py           # the one command
├── .pre-commit-config.yaml
├── logs/                     # one file per run, ignored by Git
├── .pipeline/last_run.json   # summary of the last run, ignored by Git
└── src/raviride_eta/         # stages from Module 05
```

## Part 1: predict before you run (30 minutes)

1. Open `dvc.yaml` and list, for each stage, its `cmd`, `deps`, `params`, and `outs`.
2. In a scratch file `docs/pipeline-evidence.md`, write a table with one row per change and the stages you expect to rerun:

   | Change | Stages you expect to rerun |
   |---|---|
   | edit a comment in `evaluate.py` |
   | change `params.yaml: model.max_depth` |
   | add a feature to `features.py` |
   | delete `data/features/test.csv` |
   | change `data.test_days` |

   **Checkpoint 1:** every row has an answer *before* you run anything. Keep the table; you will correct it in Part 3.

*Why first:* the value of a declared graph is that it makes predictions possible. If you run first, you learn what happened, not whether you understood the system.

## Part 2: the single command (60 minutes)

3. Write `run_pipeline.py` with:
   - `preflight()` returning a list of problems: Python version, required files, `dvc` on PATH, `params.yaml` parses;
   - argument parsing for `--check`, `--force`, `--only STAGE`, `--dry-run`;
   - a subprocess call to `dvc repro` that streams output and records it to `logs/pipeline-<timestamp>.log`;
   - exit codes `0` success, `1` pipeline failure, `2` preflight failure;
   - a JSON summary in `.pipeline/last_run.json` with command, exit code, elapsed seconds, and log path.
4. Add `logs/` and `.pipeline/` to `.gitignore`. Logs are evidence, not source.
5. Run it from the repository root:

   ```powershell
   python run_pipeline.py
   ```

   **Checkpoint 2:** exit code `0`, a log file exists, and `.pipeline/last_run.json` shows the same exit code and an elapsed time.

6. Run it from a *different* directory, using an absolute path:

   ```powershell
   cd ..
   python .\raviride-eta\run_pipeline.py
   ```

   **Checkpoint 3:** it still works. If it fails, a path is relative to the shell's current directory rather than to the project; fix it before continuing — this is the defect that breaks scheduled runs.

*Recovery:* `shutil.which("dvc")` returning `None` inside the script but working in your shell means the shell's environment is not the one running Python. Activate the environment in the same shell, or call the environment's interpreter explicitly.

## Part 3: three reruns that must behave differently (45 minutes)

7. Run again with no changes. Record the wall time and the message.
   **Checkpoint 4:** all four stages skip and the run is much faster than the first.
8. Change only `model.n_estimators` (`200` → `120`) and run. Record which stages ran.
   **Checkpoint 5:** `train` and `evaluate` run; `prepare` and `featurise` skip. Reference timing: the pipeline's evaluate line changes from MAE 2.7686 to 2.7874.
9. Restore `200` and run again. Read the output carefully.
   **Checkpoint 6:** the stages report `is cached - skipping run, checking out outputs`, and the metric returns to 2.7686 *without* retraining. Explain in your evidence file why this is not a rerun.
10. Delete `data/features/test.csv` and run.
    **Checkpoint 7:** `featurise` restores the file from cache. The pipeline does not retrain; `evaluate` also skips because its inputs are unchanged.

11. Correct your Part 1 table against what actually happened. Every wrong row is worth a sentence: which assumption was wrong?

## Part 4: break it on purpose (45 minutes)

12. Add this line to the top of `main()` in `src/raviride_eta/evaluate.py`:

    ```python
    raise RuntimeError("simulated: column traffic_index missing")
    ```

13. Run `python run_pipeline.py`. Record: the exit code, the failing stage name, and whether `metrics.json` changed.
    **Checkpoint 8:** exit code `1`; the message names `evaluate`; `metrics.json` is unchanged from the previous successful run (compare its modification time and MAE).
14. Remove the line and run again. Record which stages were skipped or restored.
    **Checkpoint 9:** nothing reruns, or only `evaluate` does, depending on whether your fixed file matches an earlier cached version. Either is correct — explain which happened.
15. Now test the data path:

    ```powershell
    Copy-Item data/raw/trips.csv data/raw/trips_good.csv
    Copy-Item data/raw/trips_bad.csv data/raw/trips.csv
    python run_pipeline.py --check
    ```

    **Checkpoint 10:** exit code `1`, three validation failures printed, and no stage ran. Restore the good file and confirm a clean run.

16. Test preflight: rename `dvc.yaml`, run the command, and confirm exit code `2` with a specific message. Restore the file.
    **Checkpoint 11:** you can state the difference between `1` and `2` in one sentence each.

## Part 5: hooks (30 minutes)

17. Install and configure `pre-commit`:

    ```powershell
    python -m pip install "pre-commit==4.0.1"
    pre-commit install
    ```

18. Add hooks for `trailing-whitespace`, `end-of-file-fixer`, `check-added-large-files` (`--maxkb=5000`), and `check-yaml`.
19. Stage a file with trailing spaces and a 6 MB file, then run `pre-commit run`.
    **Checkpoint 12:** the large file is rejected with its size, the whitespace is fixed, and no commit occurs until you re-stage.
20. Run `pre-commit run --all-files`. It must pass; fix the tree rather than skipping hooks.

## Part 6: measure and document (30 minutes)

21. Time a forced run and a cached run on your machine:

    ```powershell
    Measure-Command { dvc repro --force }
    Measure-Command { dvc repro }
    ```

    On bash: `time dvc repro --force`.
22. Time each stage individually with `python -m raviride_eta.<stage>` and put both tables in the evidence file. State the method (one run or three-run median) — a single cold run includes import time that a warm run does not.
23. Export the graph: `dvc dag --mermaid`, and paste it into the evidence file.
24. Write the runbook: the one command, expected duration, where logs go, what exit codes mean, and the three most likely failures with their first diagnostic step.
25. Commit `dvc.yaml`, `dvc.lock`, `run_pipeline.py`, `.pre-commit-config.yaml`, and the evidence file.

## Expected outputs

| Output | Reference value |
|---|---|
| Forced full run | four stages, MAE 2.7686, about 11 s wall |
| Cached run | `Data and pipelines are up to date.`, about 1.5 s |
| Parameter change | `train` + `evaluate` only; MAE 2.7874 at 120 trees |
| Revert | both stages `is cached`; MAE 2.7686 restored |
| Evaluate failure | exit `1`; prior `metrics.json` intact |
| Bad batch | exit `1`, three named failures, zero stages run |
| Missing `dvc.yaml` | exit `2`, one preflight problem |
| Large file hook | `6145 KB exceeds 5000 KB` |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| One command | A colleague can run the pipeline from a clean shell without reading the code |
| Declaration | Every file a stage reads is in `deps` or `params`; you can name one hidden input you fixed |
| Prediction | Your change → stages table matches the observed runs, with corrections explained |
| Failure handling | A failed stage stops the pipeline, preserves prior outputs, and returns non-zero |
| Recovery | You show a partial rerun and explain why each skipped stage was safe to skip |
| Evidence | Logs, timings, the graph, and the runbook contain real output, not summaries of intent |
| Hygiene | `dvc.lock` committed; `data/processed`, `data/features`, `models`, `logs` ignored |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `dvc: command not found` inside the wrapper | Environment not activated for the subprocess | Use the environment's interpreter, or activate in the same shell |
| Every stage reruns | A volatile file (log, timestamp) is in `deps` | Remove it; write logs outside the project tree |
| "Up to date" after editing a module | That module is not in any stage's `deps` | Add it to the stage that imports it |
| `Stage 'x' didn't change` but output is wrong | Output edited by hand; DVC trusts its cache | `dvc checkout` or `dvc repro --force` |
| `dvc repro` hangs | A stage is waiting on stdin | Never prompt inside a stage; read parameters from files |
| Lock file conflict | Two branches reproduced different code | Rerun `dvc repro` on the merged `dvc.yaml`; never merge hashes by hand |
| Hooks run on every commit and are slow | Heavy checks in `pre-commit` | Keep commit hooks fast; move slow checks to CI |

## Cleanup

```powershell
Remove-Item -Recurse -Force logs, .pipeline -ErrorAction SilentlyContinue
Remove-Item data/raw/trips_good.csv -ErrorAction SilentlyContinue
git status
```

Keep `dvc.yaml`, `dvc.lock`, `run_pipeline.py`, and `.pre-commit-config.yaml`. Do not delete `.dvc/cache` if you want the fast restore behaviour in later modules; it is ignored by Git either way.

## Optional extensions

1. **Fan-out.** Split training into two stages (peak and off-peak models), add a `combine` stage that reads both metric files, and make `combine` fail when one is missing. Record what happens to the graph and to the runtime.
2. **Interrupted run.** Start `dvc repro --force`, kill it during `train` (`Ctrl+C`), then rerun. Record which stages rerun and whether `models/model.joblib` is valid; explain using the cache-key rules.
3. **CI-parity command.** Add a `--ci` flag that forces a cold run, writes a JSON summary, and exits non-zero on any warning from `dvc`. Explain which of these three behaviours you would *not* want in local development, and why.

# Guided lab · Reject the bad batch, then version the good one

**Time:** 5 hours. **Tools:** Python 3.11/3.12, pandas, Git, DVC. A local directory is used as the DVC remote, so no cloud account is needed.

## Scenario and business problem

On 29 September RaviRide's trip extract gained three defects overnight: negative distances on five rows, duplicated trip identifiers, and a pickup zone `Z99` that no longer exists after a city boundary change. The training pipeline consumed all three without complaint, and the model's error rose without any code change.

Your task is to make that impossible: eight checks that reject the batch with a message the data team can act on, a leakage guard, and DVC so the clean version can be restored exactly. The business question behind the exercise is simple: *which model was trained on which data, and can we prove it?*

### Skills practised

- Writing validation as code, with named rules and actionable messages.
- Deciding between failing, filtering, and quarantining.
- Versioning a dataset by content, with a remote, and restoring it.
- Finding a leaky feature and explaining the temporal split.

### Prerequisites

Modules 02 and 03. Your repository with `src/raviride_eta/`, a working environment, and the generator available.

### Input data

Generate both batches (the generator ships with the course project):

```powershell
python scripts/generate_trips.py --out data/raw/trips.csv
python scripts/generate_trips.py --out data/raw/trips_bad.csv --corrupt
```

Expected: `wrote 1200 rows` for each. The corrupt batch is the clean batch with three planted defects, which makes it a fair test: a check that fires on everything is not a check.

### Directory layout

```text
raviride-eta/
├── data/
│   ├── raw/trips.csv
│   ├── raw/trips_bad.csv
│   ├── raw/trips.csv.dvc
│   └── README.md
├── src/raviride_eta/
│   ├── data.py          # checks + report
│   └── features.py      # leakage guard
└── docs/
    └── validation-evidence.md
```

## Part 1: the report object (30 minutes)

1. In `src/raviride_eta/data.py`, add `DataValidationError`, a `ValidationReport` dataclass with `path`, `rows`, `failures`, and methods `ok`, `render()`, `raise_if_failed()`.
2. Add a `_example(frame, mask)` helper returning `"<trip_id> (row <index>)"` for the first offending row.
3. Add a `main()` that accepts a path argument, validates it, prints the report, and returns an exit code: `0` when valid, `1` when not.
   **Checkpoint 1:** `python -m raviride_eta.data data/raw/trips.csv` prints `PASS ... 1200 rows, 8 checks` and `echo $LASTEXITCODE` (PowerShell) or `echo $?` (bash) prints `0`.

## Part 2: the eight checks (2 hours)

4. Implement the checks in this table. Every one appends to `report.failures`; none raises early.

| # | Name in the message | Rule |
|---|---|---|
| 1 | `required_columns` | All eleven expected columns present; if not, return immediately |
| 2 | `trip_id_unique` | No duplicated `trip_id` |
| 3 | `distance_km_range` | `0 < distance_km <= 60` |
| 4 | `duration_min_range` | `1 <= duration_min <= 240` |
| 5 | `pickup_zone_known` / `dropoff_zone_known` | Value in `Z01`–`Z08` |
| 6 | `counts_range` | `1 <= passengers <= 6`, `1 <= driver_supply <= 100` |
| 7 | `requested_at_window` | Timestamp parses and lies in `params.data.window_start`–`window_end` |
| 8 | `implied_speed` | `3 <= distance / (duration/60) <= 120`, computed only where distance and duration are positive |

5. For check 7, read the window from `params.yaml` rather than hard-coding dates. For check 8, skip rows already reported by checks 3 or 4 - otherwise one defect is reported twice under a misleading name.
6. Run against both batches:
   ```powershell
   python -m raviride_eta.data data/raw/trips.csv
   python -m raviride_eta.data data/raw/trips_bad.csv
   ```
   **Checkpoint 2:** the good batch passes; the bad batch reports exactly three checks, with counts 6, 5, and 4, and names example rows. If your numbers differ, your generator arguments or the window in `params.yaml` differ.
7. **Checkpoint 3:** the second command's exit code is `1`.

*Recovery:* if check 8 also fires on negative distances, you are computing speed on invalid rows. Guard with `distance.gt(0) & hours.gt(0)`.

## Part 3: document the dataset (30 minutes)

8. Compute the checksum:
   ```powershell
   (Get-FileHash data/raw/trips.csv -Algorithm MD5).Hash.ToLower()
   ```
   On bash: `md5sum data/raw/trips.csv`.
9. Write `data/README.md` with: source, generation command and seed, rows and date window, checksum, licence, known limitations (synthetic zones, one month, no real weather feed), and the sentence "what would invalidate the model trained on this data".
   **Checkpoint 4:** someone else can regenerate the file from your README and get the same checksum.

## Part 4: version the data with DVC (60 minutes)

10. Initialise DVC inside the repository and make the first commit so DVC can see a Git repository:
    ```powershell
    git add -A; git commit -m "Add validation before versioning data"
    dvc init
    git add .dvc .dvcignore; git commit -m "Initialise DVC"
    ```
11. Track the dataset:
    ```powershell
    dvc add data/raw/trips.csv
    git add data/raw/trips.csv.dvc data/raw/.gitignore
    git commit -m "Track trip extract with DVC"
    ```
    **Checkpoint 5:** `data/raw/trips.csv.dvc` contains an `md5` and `size`, and `git status` does not list the CSV.
12. Configure a local remote and push:
    ```powershell
    mkdir C:\dvcstore
    dvc remote add -d localstore C:\dvcstore
    dvc push
    ```
    Expected shape: `7 files pushed` (the count varies with what else is tracked).
13. Prove the restore:
    ```powershell
    Remove-Item data/raw/trips.csv
    dvc status
    dvc pull
    ```
    **Checkpoint 6:** `dvc status` reports the file as deleted; `dvc pull` restores it; the md5 matches the value in step 8.
14. Commit the `.dvc/config` (the remote definition) - it contains a path, not a credential.

## Part 5: the leakage guard (45 minutes)

15. In `features.py`, add `LEAKY_COLUMNS` with a reason per column (`fare_amount`: written by the meter after the trip).
16. Add a function `assert_no_leakage(feature_names: list[str])` that raises `ValueError` naming any leaky column and its reason.
17. Call it inside `split_xy` before returning the frame.
    **Checkpoint 7:** adding `fare_amount` to a feature set produces an error that says why, not just that.
18. Measure the difference for the record:
    ```python
    corr = df["fare_amount"].corr(df["duration_min"])   # 0.997 on this dataset
    ```
    Write two sentences in `docs/validation-evidence.md`: what the leaky model's error would look like, and why that number cannot be used to choose a model.
19. Confirm the split respects time: print the cut date and the min/max of each split, and state in the evidence file why a random split would inflate the score.

## Expected outputs

| Output | Value from the reference implementation |
|---|---|
| Good batch | `PASS data/raw/trips.csv: 1200 rows, 8 checks` |
| Bad batch | `FAIL ... 3 check(s) failed` with unique ids, distance, zone |
| Exit codes | `0` and `1` respectively |
| DVC pointer | `md5: 847fa5b817ba46ad0e81df2c4f273e59`, `size: 83182` |
| Restore | `dvc pull` → `1 file added`, md5 unchanged |
| Correlation | `corr(fare_amount, duration_min) = 0.997` |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Specificity | Every message names the rule, the count, and one example row |
| Coverage | All eight checks implemented, including one cross-field rule |
| Failure behaviour | The bad batch exits non-zero and is not silently filtered |
| Versioning | A clean clone with the remote configured can restore the exact bytes |
| Leakage | The guard fails on `fare_amount`, and the evidence file explains the mechanism |
| Documentation | `data/README.md` lets a stranger regenerate and identify the dataset |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ImportError: cannot import name '_DIR_MARK' from 'pathspec...'` | DVC 3.55 with pathspec 1.x | `pip install "pathspec==0.12.1"` |
| `ERROR: failed to run: python -m ...` from DVC | DVC used a different interpreter | Activate the venv before running DVC |
| `dvc push` says no remote | `dvc remote add -d` not run, or config not saved | Re-run, then `dvc remote list` |
| `dvc pull` cannot find objects | You deleted `.dvc/cache` before pushing | Regenerate with the generator, then `dvc add` again |
| Checks pass on the corrupt batch | Wrong file path, or the corrupt file was overwritten | Compare md5; regenerate with `--corrupt` |
| `ParserError` on CSV read | Hand-edited file or wrong delimiter | Regenerate; never edit data by hand |
| Pandera import fails with `cannot import name 'overload'` | `multimethod` 2.x with pandera 0.21 | `pip install "multimethod==1.12"` |

## Cleanup

- Keep `data/raw/trips_bad.csv` for Module 07's data tests; it is small.
- `dvc push` before deleting anything; the cache is not a backup.
- No services were started.

## Optional extensions

1. **Quarantine mode.** Write a variant that moves failing rows to `data/quarantine/` and fails only if more than 1% of rows fail. Explain when this is better than a hard stop.
2. **Distribution check.** Add a ninth check: the mean duration of the batch must lie within 20% of the previous batch's mean. Explain why this catches a different class of defect than the range checks, and what its false-positive risk is.
3. **Second remote.** Configure a second remote (a network drive or object storage) and show `dvc push -r` working. Read the docs for `dvc remote` rather than guessing the flags.

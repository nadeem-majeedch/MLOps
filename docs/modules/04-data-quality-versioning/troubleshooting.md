# Troubleshooting · Module 04

## DVC

**`ImportError: cannot import name '_DIR_MARK' from 'pathspec.patterns.gitwildmatch'`**

DVC 3.55.1 is incompatible with pathspec 1.x. Verified fix:

```powershell
python -m pip install "pathspec==0.12.1"
```

This is a transitive-dependency failure: nothing in your project changed, and the tool broke at run time rather than install time. Record it in your debt register under data dependencies.

**`ERROR: failed to run: python -m ...` during `dvc repro`**

DVC executes the stage command through the shell, which resolves `python` from `PATH`. If the environment is not activated in *that* shell, a different interpreter runs the stage.

Fix: activate the environment in the same terminal that runs DVC. Symptom of a mismatch: `ModuleNotFoundError: raviride_eta` from a stage that works by hand.

**`dvc push` says there is no remote, or nothing to push**

```powershell
dvc remote list
dvc status
```

If no remote is listed, `dvc remote add -d localstore C:\dvcstore` did not run or was not committed. If there is nothing to push, the cache may already be empty because the data was never added.

**`dvc pull` cannot find objects**

The remote does not contain the hash the `.dvc` file points to. Either you never pushed after the last `dvc add`, or the remote path changed. Regenerate the dataset and re-add it; do not edit the `.dvc` file by hand.

**`dvc add` complains about no Git repository**

DVC wants Git for the pointer files. Either initialise Git and commit once, or use `dvc init --no-scm` if you genuinely do not want Git. This course assumes Git.

**The data file reappears in `git status`**

`dvc add` writes an ignore rule in `data/raw/.gitignore`. If you already staged the CSV before adding, run `git rm --cached data/raw/trips.csv`, confirm the ignore file exists, and commit.

## Validation

| Symptom | Cause | Fix |
|---|---|---|
| Passes a batch you know is corrupt | Wrong path, or the corrupt file was regenerated as clean | Compare md5 before trusting the result |
| Exit code always 0 | `main()` returns nothing and nothing calls `sys.exit` | `raise SystemExit(main())` |
| `KeyError: 'trip_id'` in a message | The row lookup used `.iloc` on the wrong frame | Use `frame.loc[mask].iloc[0]` consistently |
| `TypeError` comparing string and number | Column read as `object` | `pd.to_numeric(..., errors="coerce")` before comparing |
| One defect reported three times | Per-column checks all firing on the same row | Guard later checks with the validity of earlier ones (see `implied_speed`) |
| Every batch fails after a holiday | Range check encoded as a percentile | Encode physical limits, not distributional ones |
| Timestamps shifted by hours | Local time versus UTC | Parse with an explicit time zone; store UTC in the pipeline |

## Pandera

**`ImportError: cannot import name 'overload' from 'multimethod'`**

Pandera 0.21 requires `multimethod<2`. Verified fix: `pip install "multimethod==1.12"`.

**`SchemaError` on a column that exists**

Check the dtype: `object` versus `str`, `int64` versus `float64`. Pandera checks dtypes by default; either coerce before validating or declare `coerce=True` on the column.

## When validation blocks real work

If a check fails and the data is genuinely acceptable, do not delete the check. Change it, commit the change with a reason, and note in the README which batches were accepted under which rule version. A check weakened in a panic is worse than no check, because it creates the illusion of coverage.

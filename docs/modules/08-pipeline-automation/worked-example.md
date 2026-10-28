# Worked example · One command, four runs, one failure

All output on this page comes from the course project on a laptop CPU. Paths are shortened to `data/raw/trips.csv`; DVC printed absolute paths. Your timings will differ; the *decisions* DVC makes will not.

The graph is the one from [Module 05](../05-reproducible-training/worked-example.md#the-stage-graph): `prepare → featurise → train → evaluate`.

## Run 1: forced, from a warm cache

```powershell
dvc repro --force
```

```text
Running stage 'prepare':
> python -m raviride_eta.prepare
PASS data/raw/trips.csv: 1200 rows, 8 checks
train: 896 rows 2026-09-01 02:56:00 .. 2026-09-21 23:36:00
test:  304 rows 2026-09-22 02:04:00 .. 2026-09-28 23:23:00
cutoff: 2026-09-22 00:00:00

Running stage 'featurise':
> python -m raviride_eta.featurise
train: 896 rows, added ['hour', 'day_of_week', 'is_weekend', 'is_peak', 'log_distance'] -> train.csv
test:  304 rows, added ['hour', 'day_of_week', 'is_weekend', 'is_peak', 'log_distance'] -> test.csv

Running stage 'train':
> python -m raviride_eta.train
trained full model on 896 rows -> model.joblib

Running stage 'evaluate':
> python -m raviride_eta.evaluate
test rows: 304
MAE 2.7686 min | RMSE 4.4922 | R2 0.7319 | p95 8.254 min
wrote metrics.json
```

`--force` is the honest way to answer "does this still run?" It bypassed the cache for every stage. Wall-clock time for the whole command: **11.2 s**. The stages themselves, measured separately with `python -m raviride_eta.<stage>`:

| Stage | Wall time |
|---|---|
| `prepare` | 0.61 s |
| `featurise` | 0.62 s |
| `train` | 2.10 s |
| `evaluate` | 1.58 s |
| Sum of stages | 4.91 s |
| Whole `dvc repro` | 11.17 s |

The 6-second gap is DVC's own start-up and hashing, not machine learning. That matters for the independent challenge: at this scale, optimising the model is the wrong lever; changing how often the pipeline runs is the right one.

## Run 2: nothing changed

```text
Stage 'prepare' didn't change, skipping
Stage 'featurise' didn't change, skipping
Stage 'train' didn't change, skipping
Stage 'evaluate' didn't change, skipping
Data and pipelines are up to date.
```

Measured wall time: **1.5 s**. No output was recomputed, and none needed to be: the lock file's keys match the current inputs.

## Run 3: one parameter changes

`model.n_estimators` goes from `200` to `120`.

```text
Stage 'prepare' didn't change, skipping
Stage 'featurise' didn't change, skipping
Running stage 'train':
> python -m raviride_eta.train
trained full model on 896 rows -> model.joblib
Running stage 'evaluate':
> python -m raviride_eta.evaluate
test rows: 304
MAE 2.7874 min | RMSE 4.5016 | R2 0.7308 | p95 8.4465 min
wrote metrics.json
```

Exactly two stages ran. `prepare` and `featurise` do not read `model.*`, so their keys are unchanged. The metric moved by 0.019 minutes — small, and not evidence that 120 trees is "as good": Module 06's slice analysis is what decides whether a difference of that size matters.

## Run 4: revert, and watch the cache restore instead of retrain

Restoring `n_estimators: 200` could rerun training. It does not:

```text
Stage 'prepare' didn't change, skipping
Stage 'featurise' didn't change, skipping
Stage 'train' is cached - skipping run, checking out outputs
Stage 'evaluate' is cached - skipping run, checking out outputs
```

`metrics.json` is back to MAE **2.7686** without the forest being fitted again. The cache key for the 200-tree configuration already existed, so DVC copied the matching outputs out of `.dvc/cache`.

Two lessons, both easy to miss:

- **Reverting a parameter reverts the artefact**, provided the cache was not cleared. This is a fast, reliable undo — and a trap if you believed "repro" always means "rerun".
- **Cache hits are not verification.** If `train.py` had a bug that only manifests on a cold cache, this run would not find it. That is why release pipelines use `--force` or a clean clone.

## Run 5: a stage fails

A simulated upstream schema change raises inside `evaluate`:

```text
Stage 'prepare' didn't change, skipping
Stage 'featurise' didn't change, skipping
Stage 'train' didn't change, skipping
Running stage 'evaluate':
> python -m raviride_eta.evaluate
Traceback (most recent call last):
  ...
RuntimeError: simulated upstream schema change: column traffic_index missing
ERROR: failed to reproduce 'evaluate': failed to run: python -m raviride_eta.evaluate, exited with 1
```

What the state is afterwards — this is the part to be able to recite:

| Question | Answer |
|---|---|
| Which stage failed? | `evaluate`; the message names it twice |
| Did earlier stages rerun? | No; `train` was skipped, so the model is the previous good artefact |
| Is `metrics.json` valid? | It is the previous run's file. It was not overwritten |
| Did `dvc repro` report success? | No; the shell saw a non-zero exit (255 on DVC 3.59), and the message records the stage's own exit code `1` |
| What will the next run do? | Skip `prepare`–`train`, rerun `evaluate` once the cause is fixed |

The failed stage's own exit code is `1` because an uncaught Python exception exits `1`. DVC's non-zero exit is what a wrapper or CI system keys on.

## Run 6: recovery

After fixing `evaluate.py` and running `dvc repro`:

```text
Stage 'prepare' didn't change, skipping
Stage 'featurise' didn't change, skipping
Stage 'train' didn't change, skipping
Stage 'evaluate' is cached - skipping run, checking out outputs
```

Because the fixed file matches the content used in the successful Run 1, the result is *already in the cache*: DVC restores the metrics rather than recomputing them. A reviewer may find that unsatisfying — "I fixed it, and nothing ran". It is correct: the inputs are byte-identical to a known-good run. If you want proof that the fix executes, change something real or use `--force`.

## Run 7: failures the wrapper catches before DVC starts

The entry point separates preflight problems from pipeline problems.

A corrupt batch, with `--check`:

```text
FAIL data/raw/trips.csv: 1200 rows, 8 checks
  - trip_id_unique: 5 duplicated ids, first T000450 (row 599)
  - distance_km_range: 6 rows outside (0, 60], first T000242 (row 693)
  - pickup_zone_known: 4 rows with unknown zones ['Z99'], first T000445 (row 603)
data validation rejected the batch; nothing was trained
```

Exit code: `1`. Note what did *not* happen: no stage ran, so no artefact was replaced. Validation inside `prepare` would also have stopped the pipeline, but only after DVC had started and `prepare` had produced a failure trace; checking first keeps the failure cheap and the message short.

A missing `dvc.yaml`:

```text
PREFLIGHT FAILED
  - missing required file: dvc.yaml
```

Exit code: `2`. The distinction is operational: a scheduler can page the data team for `2` (environment or inputs) and the ML engineer for `1` (the pipeline itself).

## Run 8: the hook that stops a commit

With `pre-commit install` and the configuration in [Concepts §9](concepts.md#9-commit-time-hooks), staging a 6 MB CSV and a file with trailing spaces gives:

```text
trim trailing whitespace.................................................Failed
- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing scratch.md

fix end of files.........................................................Failed
- hook id: end-of-file-fixer
- exit code: 1
- files were modified by this hook

Fixing big_dump.csv

check for added large files..............................................Failed
- hook id: check-added-large-files
- exit code: 1

big_dump.csv (6145 KB) exceeds 5000 KB.

check yaml...............................................................Passed
```

The large file is rejected; the whitespace problems are repaired in place. The commit does not happen until the staging area is refreshed. `pre-commit run --all-files` on a clean tree exits `0`, which is the state you want before opening a pull request.

## What the eight runs establish

| Claim | Evidence |
|---|---|
| One stage graph can answer "what is stale" | Runs 2–4 |
| A rerun does the minimum correct work | Run 3 ran two of four stages |
| Reverting a parameter restores the earlier artefact | Run 4, metrics returned to 2.7686 |
| Failure stops the pipeline and preserves prior outputs | Run 5 |
| Recovery is partial, not total | Run 6 |
| Preflight failures are distinguishable from pipeline failures | Run 7, exit `1` vs `2` |
| Cheap checks belong before the commit exists | Run 8 |

The remaining risk is the one no cache can address: every stage ran against your installed packages. Module 11 makes the environment part of the declaration.

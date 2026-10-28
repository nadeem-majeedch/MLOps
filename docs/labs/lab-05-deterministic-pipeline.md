# Lab 05 · Make a pipeline deterministic, then make it lazy

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L05 | Intermediate | 4 hours | [05 · Reproducible training](../modules/05-reproducible-training/index.md), [08 · Pipeline automation](../modules/08-pipeline-automation/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-05-deterministic-pipeline/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-05-deterministic-pipeline) — starter files, data generator, and acceptance checker.

## Scenario

Your three-stage pipeline produces a slightly different MAE on every run. Nobody
notices until a candidate is compared with the champion and wins by 0.02 — less
than the pipeline's own noise. At the same time, a full rerun takes long enough
that people skip it, which is how stale features reach a model.

Two changes, one artefact: stage outputs must be a pure function of their inputs,
and a stage whose inputs have not changed must not run again.

## What you will be able to do

- Identify nondeterminism that survives a seeded model: ordering, sampling,
  float formatting, and set iteration.
- Design a cache key from content rather than from timestamps.
- Invalidate exactly the stages a parameter change affects.
- Show that a warm rerun is faster without being different.

## Prerequisites and setup

```bash
cd examples/labs/lab-05-deterministic-pipeline
python ../_shared/make_sessions.py --out data/sessions.csv
python pipeline.py
python pipeline.py
```

Compare `artifacts/manifest.json` between the two runs. Expected: the `review`
list, the feature order, the MAE or all three differ.

## Your task

Make the pipeline deterministic under any hash seed, then implement the stage
cache and the `--reuse` flag. `check_lab05.py` runs the whole cycle.

## Data and starter files

| File | Purpose |
|---|---|
| `pipeline.py` | Three stages, two defects, no cache |
| `check_lab05.py` | Runs twice cold, once warm, once with a changed parameter |
| `data/sessions.csv` | 480 sessions |

The manifest contract:

```json
{"stages": [{"name": "prepare", "key": "…", "status": "computed", "rows": 480},
            {"name": "features", "key": "…", "status": "computed", "rows": 480},
            {"name": "train", "key": "…", "status": "computed", "rows": 480}],
 "metrics": {"mae": 4.926165, "predictions_sha256": "77c1b222…", "review": ["S0074", "S0415", "S0395"]},
 "features": ["hours", "prior_score", "sleep_hours", "study_ratio"]}
```

## Steps

### 1. Find the three sources of variation

Run the starter under two hash seeds:

```bash
PYTHONHASHSEED=0 python pipeline.py > a.json
PYTHONHASHSEED=1 python pipeline.py > b.json
diff a.json b.json
```

PowerShell:

```powershell
$env:PYTHONHASHSEED = "0"; python pipeline.py > a.json
$env:PYTHONHASHSEED = "1"; python pipeline.py > b.json
```

```powershell
$env:PYTHONHASHSEED="0"; python pipeline.py > a.json
$env:PYTHONHASHSEED="1"; python pipeline.py > b.json
Compare-Object (Get-Content a.json) (Get-Content b.json)
```

You should see the split-driven MAE change, the unseeded review sample, and the
feature order (because `make_features` iterates a set).

### 2. Fix ordering first

Sort feature names and sort rows on a unique key with a stable sort. Ordering
bugs are the ones that survive seeding, so fix them before you look at the
metric.

### 3. Seed what samples

`train_test_split(random_state=...)` and `sample(random_state=...)`. Round the
metric once, at the boundary, not at every intermediate step.

### 4. Design the cache key

A stage key must change when its inputs or its parameters change, and must not
change when a file is merely touched. Hash a canonical representation:

```text
sha256(stage name, upstream key, stage parameters, code version)
```

Store frame outputs as CSV and the train metrics as JSON under `.cache/`. Record
`status` as `hit` or `computed` in the manifest.

### 5. Verify partial invalidation

```bash
python pipeline.py --reuse                       # expect hit, hit, hit
python pipeline.py --reuse --trees 60            # expect hit, hit, computed
```

Expected MAE at 120 trees: `4.926165`. At 60 trees: `4.899642`. The second run
must not re-run prepare or features.

### 6. Run the checker

```bash
python check_lab05.py
```

Expected: `12/12 checks passed`.

## Expected output

```text
  [PASS] metrics are identical under a different hash seed -- got 4.926165, expected 4.926165
  [PASS] predictions are identical -- got '77c1b222fabde718...'
  [PASS] the review sample is identical -- got ['S0074', 'S0415', 'S0395']
  [PASS] feature order is identical -- got ['hours', 'prior_score', 'sleep_hours', 'study_ratio']
  [PASS] every stage computed on a cold run -- ['computed', 'computed', 'computed']
  [PASS] an unchanged rerun reuses every stage -- ['hit', 'hit', 'hit']
  [PASS] changing the trees parameter recomputes only train -- got ['hit', 'hit', 'computed']
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Two cold runs agree | Identical metrics, predictions and review list |
| 2 | Feature order is stable | Same list under both hash seeds |
| 3 | Stage keys are content-derived | Non-empty and different per stage |
| 4 | Warm rerun reuses all stages | Three `hit` entries |
| 5 | Parameter change invalidates only train | `hit, hit, computed` |
| 6 | Changed parameter changes the metric | Different MAE |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| MAE still differs between seeds | Unseeded `sample` or `shuffle` | Search for `random_state` omissions |
| Warm run reports `computed` | Cache key includes a timestamp or PID | Hash only content and parameters |
| Warm run loads the wrong features | Cache key does not include upstream key | Chain keys: each stage includes its parent's |
| CSV cache loses dtypes | `to_csv` round-trip | Restore dtypes explicitly, or cache parquet |
| `--trees` change re-runs everything | Code version is not part of the key but parameters are global | Include only the stage's own parameters |

## Reflection questions

1. Why is a file modification time a poor cache key, even on one machine?
2. Your cache is content-addressed but the code changed. What happens, and what
   should happen?
3. Which stage is worth caching most, and what does the answer depend on?
4. What would you need to add before this cache is safe for two engineers on the
   same machine?

## Optional extension

Add a `--clean` flag that removes cache entries older than seven days, and a
`--stats` report showing hits, misses and time saved. Then measure a real
three-run cycle and record the numbers.

## Cleanup

```bash
rm -rf .cache artifacts data
```

PowerShell: `Remove-Item .cache, artifacts, data -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I identified all three sources of variation
- [ ] Two cold runs produce identical artefacts
- [ ] Stage keys are built from content and parameters
- [ ] A warm run reports three hits
- [ ] A parameter change recomputes only `train`
- [ ] `check_lab05.py` reports `ACCEPTED`

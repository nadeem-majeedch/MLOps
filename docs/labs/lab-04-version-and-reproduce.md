# Lab 04 · Version a dataset and reproduce last month's run

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L04 | Intermediate | 3 hours | [04 · Data quality and versioning](../modules/04-data-quality-versioning/index.md), [05 · Reproducible training](../modules/05-reproducible-training/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-04-dataset-versioning/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-04-dataset-versioning) — starter files, data generator, and acceptance checker.

## Scenario

A reviewer asks you to reproduce the model that was reported on 21 September.
You still have the code, the environment file and the metrics. You do not have
the data: the extract was overwritten a week later, and the file name never
changed. `train.csv` is not a version, it is a slot.

You will build the smallest thing that answers the question: a content hash
recorded with the shape of the data, and a training script that refuses to run
when the bytes on disk are not the bytes the run claims.

## What you will be able to do

- Explain why a filename and a date are not a dataset version.
- Record a manifest that is sufficient to detect in-place edits.
- Make a training script fail closed when the data does not match its manifest.
- Show that two runs from the same manifest agree.

## Prerequisites and setup

```bash
cd examples/labs/lab-04-dataset-versioning
python ../_shared/make_sessions.py --out data/sessions.csv
python version_data.py --data data/sessions.csv --tag v1
```

Expected: `v1: 480 rows sha256=979c7d7abb8df4bc... -> data/manifests/v1.json`.
Your hash will differ only if the generator changed; it is deterministic.

## Your task

Implement the three missing functions in `reproduce.py`: verify the manifest,
train, and return a run record. `check_lab04.py` drives the whole scenario.

## Data and starter files

| File | Purpose |
|---|---|
| `version_data.py` | Complete manifest writer (hash, rows, dtypes, null counts) |
| `reproduce.py` | Skeleton: `verify_manifest` and `train_and_record` raise |
| `check_lab04.py` | Builds two versions, reproduces v1 twice, then tampers |

## Steps

### 1. Read the manifest

```bash
cat data/manifests/v1.json
```

PowerShell: `Get-Content data/manifests/v1.json`.

It contains the tag, the path, the SHA-256 of the bytes, the row count, column
dtypes and null counts. Note what it does not contain: the file name is stored,
but nothing about the name is treated as identity.

### 2. Reproduce v1

Implement `verify_manifest` so that a hash mismatch prints `hash mismatch` and
exits with code 2. Then implement `train_and_record` so the run record contains
`tag`, `sha256`, `rows`, `seed`, `mae` and `predictions_sha256`.

```bash
python reproduce.py --manifest data/manifests/v1.json
```

Run it twice and compare the two run records: identical MAE is expected, and so
is an identical predictions hash.

### 3. Create a second version

Append one row and tag it:

```bash
echo "S9001,A,3.5,64.0,7.1,71.2" >> data/sessions.csv
python version_data.py --data data/sessions.csv --tag v2
```

v2 has 481 rows and a different hash. The v1 manifest still exists, and it is
now wrong about the file on disk.

### 4. Watch the script refuse

```bash
python reproduce.py --manifest data/manifests/v1.json; echo $?
```

Expected: `hash mismatch: ... is bc24e4... , manifest v1 expects 979c7d...` and
exit code 2. No run record is written. This refusal is the feature; a script
that trains anyway is how a "reproduced" number becomes fiction.

### 5. Run the checker

```bash
python check_lab04.py
```

Expected: `15/15 checks passed`.

Restore the data afterwards if you want to keep a clean state:

```bash
git checkout -- data/sessions.csv   # or regenerate it
```

## Expected output

```text
  [PASS] version_data.py writes a manifest -- no stderr
  [PASS] manifest hash is the hash of the bytes -- got '979c7d7abb8df4bc...'
  [PASS] manifest records the row count -- got 480, expected 480
  [PASS] manifest records column types -- 6 columns
  [PASS] reproduction 1 trains from v1 -- no stderr
  [PASS] reproduction 2 trains from v1 -- no stderr
  [PASS] two reproductions report the same mae -- got 4.901629, expected 4.901629
  [PASS] two reproductions report the same predictions hash -- ...
  [PASS] stale manifest is refused with exit 2 -- got 2, expected 2
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Manifest hash equals the file hash | Exact match |
| 2 | Manifest records rows, dtypes and nulls | Present |
| 3 | Two reproductions from one manifest agree | Same MAE and predictions hash |
| 4 | A changed dataset is rejected | Exit 2, message contains `hash mismatch` |
| 5 | No run record is written on rejection | Absent |
| 6 | A second tag records the new content | Different hash, row count 481 |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Hash differs between machines | File line endings changed by Git | Add `.gitattributes` with `* text=auto eol=lf`, or hash parsed data instead |
| `SystemExit` returns 1 instead of 2 | Passing a string to `SystemExit` | Print the message, then `raise SystemExit(2)` |
| MAE differs between reproductions | Unseeded split or sampled rows | Seed the split and any sampling |
| `predictions_sha256` differs but MAE matches | Hashing floats after JSON round-trip | Hash `predictions.round(6).tobytes()` |
| Manifest path invalid on another machine | Absolute path recorded | Record a project-relative path |

## Reflection questions

1. The manifest stores a hash and a path. Which of the two is the version, and
   why keep the other one at all?
2. What does this scheme not prove? Name one thing an attacker or an accident
   could still change.
3. Why is `hash mismatch` a better failure than "training on the latest data"?
4. If the CSV is 4 GB, is hashing the bytes still the right check? What would you
   do instead?

## Optional extension

Replace the hand-written manifest with DVC (`dvc add data/sessions.csv`) and
compare what DVC records with what your manifest records. Note in one paragraph
which fields DVC adds and which of yours are redundant.

## Cleanup

```bash
rm -rf data/manifests runs data/versioned_drop.csv
```

PowerShell: `Remove-Item data/manifests, runs, data/versioned_drop.csv -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I created v1 and reproduced it twice with identical results
- [ ] I created v2 and saw the hash change
- [ ] The stale manifest was refused with exit code 2
- [ ] No run record was produced by the refused run
- [ ] `check_lab04.py` reports `ACCEPTED`

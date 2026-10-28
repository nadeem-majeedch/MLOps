# Lab 09 · Track artefacts, promote one, roll back under pressure

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L09 | Intermediate | 3 hours | [09 · Model registry and lifecycle](../modules/09-model-registry/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-09-release-candidates/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-09-release-candidates) — starter files, data generator, and acceptance checker.

## Scenario

You have four registered candidates and one `champion` alias. The gate from Lab
08 decides who may move the alias. This lab is about what happens around the
decision: version metadata, promotion lineage, and the rollback you need at 2am
when the new champion turns out to be wrong.

A registry is not a folder of `.joblib` files. It is a record of what was
released, when, by which run, and what it replaced.

## What you will be able to do

- Register a model version with tags that answer "which data, which run?".
- Move an alias only after a gate, and record where it came from.
- Roll back without remembering the previous version yourself.
- Read a version history that survives the person who created it.

## Prerequisites and setup

```bash
cd examples/labs/lab-09-release-candidates
python lifecycle.py register candidates/baseline_v1.json
python lifecycle.py show
```

MLflow uses the local `mlruns/` store. No server and no account are needed. The
registered artefact is a small real model, so loading a version is a real
operation rather than a file copy.

## Your task

Implement `gate`, `promote` and `rollback` in `lifecycle.py`. The checker
registers four candidates, promotes one, blocks two and rolls back.

## Data and starter files

| File | Purpose |
|---|---|
| `lifecycle.py` | Register is complete; gate/promote/rollback raise |
| `candidates/*.json` | Four candidate records with metrics and metadata |
| `policy.yaml` | Same rules as Lab 08, applied to the registry |
| `check_lab09.py` | Full lifecycle, verified against the MLflow client |

## Steps

### 1. Register and inspect

```bash
python lifecycle.py register candidates/baseline_v1.json
python lifecycle.py register candidates/deeper_v2.json
python lifecycle.py show
```

Each version carries `candidate`, `data_hash`, `run_id` and `dropped_zones`. The
`run_id` is the link back to metrics and artefacts; without it a version is a
number.

### 2. Promote the champion

```bash
python lifecycle.py promote 1
```

Expected: `champion -> v1 (was vNone)`, and `promoted_from` set to `none`. The
first promotion has no predecessor, and saying so explicitly is better than
leaving the field empty.

### 3. Block a bad candidate

```bash
python lifecycle.py promote 3
```

`shallow_v3` fails the absolute ceiling. Expected: exit 1, reasons printed, alias
unchanged. A gate that blocks but moves the alias anyway is worse than no gate.

### 4. Promote the good one

```bash
python lifecycle.py promote 2
```

Expected: `champion -> v2 (was v1)`, with `promoted_from = 1`. That single tag is
what makes an unattended rollback possible.

### 5. Roll back

```bash
python lifecycle.py rollback
python lifecycle.py rollback --to 4
```

The first returns to `promoted_from` (v1) and tags `rollback_at`. The second moves
to an explicit version, which is what you do when the previous champion was also
bad.

### 6. Run the checker

```bash
python check_lab09.py
```

Expected: `25/25 checks passed`.

## Expected output

```text
  [PASS] four versions are registered -- got 4, expected 4
  [PASS] every version carries its data hash and run id -- [['candidate', 'data_hash', 'dropped_zones', 'run_id']]
  [PASS] a model artifact exists for a version -- ['model/MLmodel', ...]
  [PASS] an underfitted candidate is blocked -- exit 1
  [PASS] the alias did not move -- got 1, expected 1
  [PASS] the zone block names the zone -- BLOCKED v4: - zone Z01 mae 2.190 ... allowed 1.984
  [PASS] v2 remembers it replaced v1 -- got '1', expected '1'
  [PASS] rollback succeeds without being told the target -- rolled back: v2 -> v1
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Four versions registered | 4 |
| 2 | Every version has `data_hash` and `run_id` | Present |
| 3 | A loadable model artefact exists | `model/MLmodel` |
| 4 | Blocked promotion leaves the alias untouched | v1 remains champion |
| 5 | Promotion records its predecessor | `promoted_from` |
| 6 | Rollback needs no arguments | Returns to the recorded predecessor |
| 7 | Rolled-back version is tagged | `rollback_at` present |
| 8 | History file matches the registry | Champion and chain |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `RESOURCE_DOES_NOT_EXIST` on alias | Tracking URI differs between commands | Always use the resolved `mlruns` URI |
| Version numbers restart at 1 | `mlruns/` deleted between commands | Register all versions in one session |
| Alias moves despite a block | Gate result ignored before `set_registered_model_alias` | Return 1 before any write |
| `promoted_from` is empty | Tag set after the alias, or not at all | Tag and alias in the same successful path |
| `mlflow.register_model` slow first time | Artefact copy into the store | Expected; subsequent calls are faster |

## Reflection questions

1. Why keep the artefact in the registry rather than pointing at a path on the
   training machine?
2. `promoted_from` is a tag, not a foreign key. What could go wrong, and what
   would a stricter registry give you?
3. Should rollback run the gate? Argue both sides in two sentences each.
4. What belongs in a version's tags so that an auditor can answer "why was this
   released?" without reading chat history?

## Optional extension

Add a `--dry-run` flag to `promote` that prints the gate result and the alias
change without writing. Then add a `history` command that prints every promotion
and rollback in time order, derived from tags.

## Cleanup

```bash
rm -rf mlruns artifacts
```

PowerShell: `Remove-Item mlruns, artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] Every version is traceable to a run and a dataset hash
- [ ] A blocked candidate cannot move the alias
- [ ] Promotion records its predecessor
- [ ] Rollback works with no arguments
- [ ] `check_lab09.py` reports `ACCEPTED`

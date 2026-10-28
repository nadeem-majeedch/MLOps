# Lab 16 · Schedule, retry, and backfill a training workflow

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L16 | Advanced | 4 hours | [13 · Workflow orchestration](../modules/13-orchestration/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-16-orchestration/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-16-orchestration) — starter files, data generator, and acceptance checker.

## Scenario

The nightly job has run unattended for three weeks. Last Tuesday the staging
table was locked for four seconds, the transform failed, and nobody noticed until
a report was missing at noon. On Wednesday someone re-ran the job by hand, which
trained the same date twice and overwrote the artefact that had already been
reviewed.

A scheduled pipeline needs three properties that a script does not: a retry
policy, a state file, and an idempotent way to fill gaps.

## What you will be able to do

- Retry transient failures with growing backoff and give up on permanent ones.
- Record per-date state that answers "did last night run?" without timestamps.
- Make a backfill safe to repeat.
- Decide what counts as transient.

## Prerequisites and setup

```bash
cd examples/labs/lab-16-orchestration
python make_data.py
python flow.py --date 2026-09-20
```

Expected: 1,800 rows across 30 days, then `2026-09-20: succeeded in 0.018s`.
The starter has no retry, no skip and no attempt history.

## Your task

Rewrite `run()` in `flow.py` to retry, record every attempt and skip completed
dates; keep `backfill` reporting what it actually did. `check_lab16.py` drives
transient failures, exhausted retries, replays and backfills.

## Data and starter files

| File | Purpose |
|---|---|
| `flow.py` | Three tasks, state, CLI (`--date`, `--backfill`, `--force`) |
| `make_data.py` | 1,800 dated sessions, 30 days |
| `check_lab16.py` | Retry, exhaustion, idempotency and backfill checks |

Fault injection: `FLAKY_ATTEMPTS=n` makes `transform` fail `n` times per date
before succeeding. `MAX_ATTEMPTS` defaults to 3.

State contract, one file per date at `.state/<date>.json`:

```json
{"date": "2026-09-20", "status": "succeeded",
 "attempts": [{"n": 1, "error": "staging table locked...", "wait_s": 0.2},
              {"n": 2, "error": null, "wait_s": 0.0}],
 "outputs": {"features": "runs/2026-09-20/features.csv", "metrics": "..."},
 "elapsed_s": 0.41, "finished_at": "..."}
```

## Steps

### 1. Make a transient failure visible

```bash
FLAKY_ATTEMPTS=1 python flow.py --date 2026-09-20
```

```powershell
$env:FLAKY_ATTEMPTS="1"; python flow.py --date 2026-09-20; Remove-Item Env:\FLAKY_ATTEMPTS
```

The starter fails on the first attempt and records one failed attempt. Nothing
retries, and the date is still missing the next morning.

### 2. Retry only what deserves it

Catch `TransientError` and retry; let other exceptions fail the run immediately.
Retrying a `ValueError` from an empty extract wastes three attempts and delays the
alert.

### 3. Back off and record the wait

`wait = base * 2 ** (attempt - 1)` with `base=0.2`. Record the wait on the failed
attempt so the state file explains the gap in the timeline. Expected waits:
`0.2`, `0.4`.

### 4. Exhaust honestly

```bash
FLAKY_ATTEMPTS=9 MAX_ATTEMPTS=3 python flow.py --date 2026-09-21
```

```powershell
$env:FLAKY_ATTEMPTS="9"; $env:MAX_ATTEMPTS="3"; python flow.py --date 2026-09-21
Remove-Item Env:\FLAKY_ATTEMPTS, Env:\MAX_ATTEMPTS
```

Expected: exit 1, three attempts recorded, the last one carrying the error. A
failed date is allowed; an unrecorded failure is not.

### 5. Skip completed work

Run the same date again with no faults:

```bash
python flow.py --date 2026-09-20
```

Expected: `skipped (already complete on ...)`, and the metrics file unchanged.
Overwriting a reviewed artefact with an identical one is harmless today and
harmful the day the data drifts between runs.

### 6. Backfill twice

```bash
python flow.py --backfill 2026-09-18:2026-09-19
python flow.py --backfill 2026-09-18:2026-09-19
```

First run: two dates complete. Second run: two skips, no new work, no duplicated
runs. `--force` is the explicit way to redo a date.

### 7. Run the checker

```bash
python check_lab16.py
```

Expected: `21/21 checks passed`.

## Expected output

```text
  [PASS] a transient failure is retried and succeeds -- 2026-09-20: succeeded after 2 attempt(s)
  [PASS] the first attempt recorded the transient error -- {'n': 1, 'error': 'staging table locked ...', 'wait_s': 0.2}
  [PASS] the retry waited before running -- 0.2
  [PASS] a completed date is skipped, not retrained -- 2026-09-20: skipped (already complete ...)
  [PASS] exactly three attempts were made -- got 3, expected 3
  [PASS] backoff grows between attempts -- waits [0.2, 0.4]
  [PASS] a repeated backfill duplicates no work -- metrics unchanged
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Transient failure retried | Two attempts, success |
| 2 | Failure recorded with its error | First attempt has `error` |
| 3 | Wait grows | Attempt 1 wait > 0, attempt 2 wait larger on the failed run |
| 4 | Retries exhausted | Exit 1 after exactly 3 attempts |
| 5 | Completed date skipped | stdout contains `skipped` |
| 6 | Artefact not overwritten | Metrics hash unchanged |
| 7 | `--force` reruns | Attempt count resets, new `finished_at` |
| 8 | Backfill fills gaps | Both dates succeeded |
| 9 | Repeated backfill is a no-op | No duplicated work |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Retry never happens | `transform` raises a plain `RuntimeError` | Catch `TransientError` explicitly |
| Wait is always 0 | Backoff computed after `sleep` | Compute, record, then sleep |
| Second run retrains | `status` compared but not stored | Check `load_state(day)["status"]` |
| Backfill reports success but dates missing | Counting attempted rather than completed | Count `status == "succeeded"` |
| `--force` still skips | Force flag not passed into `run` | Thread it through `backfill` |

## Reflection questions

1. Which failures in your own pipelines are transient, and how would you know?
2. Why does the state file record attempts rather than only the final status?
3. Idempotency here means "skip if succeeded". What would idempotency mean for a
   task that must always run, such as sending a report?
4. When would you want a backfill to retrain a completed date automatically?

## Optional extension

Add a `--deadline` option that stops the backfill after a wall-clock limit and
reports which dates remain, then explain why a nightly job needs a deadline even
when every task has a timeout.

## Cleanup

```bash
rm -rf .state runs data
```

PowerShell: `Remove-Item .state, runs, data -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] A transient failure is retried with growing backoff
- [ ] Exhausted retries leave an honest failed state
- [ ] Completed dates are skipped, including during backfill
- [ ] `--force` is the only way to redo a date
- [ ] `check_lab16.py` reports `ACCEPTED`

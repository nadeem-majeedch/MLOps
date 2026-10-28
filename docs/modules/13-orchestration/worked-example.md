# Worked example · A scheduler small enough to read, honest enough to be useful

`orchestration/scheduler.py` is about 120 lines. It runs five tasks in dependency order, records every attempt, retries with exponential backoff, and treats the logical date as the unit of work.

## The definition

```python
@dataclass
class Task:
    name: str
    module: str
    deps: list[str] = field(default_factory=list)
    retries: int = 0
    backoff_s: float = 1.0

TASKS = [
    Task("validate",  "raviride_eta.data",      deps=[],           retries=0),
    Task("prepare",   "raviride_eta.prepare",   deps=["validate"], retries=1),
    Task("featurise", "raviride_eta.featurise", deps=["prepare"],  retries=1),
    Task("train",     "raviride_eta.train",     deps=["featurise"],retries=2),
    Task("evaluate",  "raviride_eta.evaluate",  deps=["train"],    retries=1),
]
```

Two deliberate choices:

- **Retries differ by task.** `validate` has none: re-reading a malformed file cannot fix it. `train` has two: memory pressure and transient dependency failures are plausible and worth another attempt.
- **The date is a parameter, not `now()`.** `--date 2026-09-29` is a complete description of the work, which is what makes re-runs and backfills possible.

State is one JSON file per logical date:

```text
.orchestrator/2026-09-29.json
runs/2026-09-29/metrics.json
```

## Run 1: a transient failure that recovers

The scheduler was asked to make `train` fail once:

```powershell
python orchestration/scheduler.py --date 2026-09-29 --inject train --inject-times 1
```

```text
[2026-09-29] validate: success on attempt 1 in 0.55s
[2026-09-29] prepare: success on attempt 1 in 0.53s
[2026-09-29] featurise: success on attempt 1 in 0.55s
[2026-09-29] train: attempt 1 failed (simulated transient failure (attempt 1 of 1)); retrying in 1.0s
[2026-09-29] train: success on attempt 2 in 2.29s
[2026-09-29] evaluate: success on attempt 1 in 1.54s
[2026-09-29] run complete -> runs/2026-09-29/metrics.json
```

Three facts to read from it:

- The failure was **classified as transient** by the retry policy; a schema error would have exhausted the attempts and failed the run.
- The retry waited **1.0 s** (the base backoff, doubled per attempt for higher retry counts). Production schedules use minutes, not seconds, but the mechanism is the same.
- Only `train` and its child reran. `validate`, `prepare`, and `featurise` were not repeated.

## Run 2: the same date again

```powershell
python orchestration/scheduler.py --date 2026-09-29
```

```text
[2026-09-29] run already complete and outputs present; nothing to do (idempotent)
```

This is the property that makes a scheduler safe to poke: the run is keyed by logical date, its state says `success`, and its output exists. Nothing is recomputed and nothing is duplicated.

Note what the check requires: **both** the state and the output file. A state file claiming success while `runs/2026-09-29/metrics.json` is missing indicates someone deleted the output, and the run should be redone rather than trusted.

## Run 3: a failure that exhausts its retries

`evaluate` was made to fail persistently:

```powershell
python orchestration/scheduler.py --date 2026-09-30 --inject evaluate --inject-times 5
```

```text
[2026-09-30] validate: success on attempt 1 in 0.54s
[2026-09-30] prepare: success on attempt 1 in 0.55s
[2026-09-30] featurise: success on attempt 1 in 0.55s
[2026-09-30] train: success on attempt 1 in 2.03s
[2026-09-30] evaluate: attempt 1 failed (simulated transient failure (attempt 1 of 5)); retrying in 1.0s
[2026-09-30] evaluate: FAILED after 2 attempts: simulated transient failure (attempt 2 of 5)
```

Exit code `1`. The state file records exactly what survived:

```json
{
  "run_date": "2026-09-30",
  "tasks": {
    "validate":  {"status": "success", "attempts": 1, "duration_s": 0.54},
    "prepare":   {"status": "success", "attempts": 1, "duration_s": 0.55},
    "featurise": {"status": "success", "attempts": 1, "duration_s": 0.55},
    "train":     {"status": "success", "attempts": 1, "duration_s": 2.03},
    "evaluate":  {"status": "failed",  "attempts": 2, "last_error": "..."}
  },
  "status": "failed"
}
```

The run did not write `runs/2026-09-30/metrics.json`, because the final step never succeeded. That is the correct outcome: a date with a failed evaluation should not look complete to a consumer.

## Run 4: resume

```powershell
python orchestration/scheduler.py --date 2026-09-30
```

```text
[2026-09-30] validate: already succeeded, skipping
[2026-09-30] prepare: already succeeded, skipping
[2026-09-30] featurise: already succeeded, skipping
[2026-09-30] train: already succeeded, skipping
[2026-09-30] evaluate: success on attempt 1 in 1.54s
[2026-09-30] run complete -> runs/2026-09-30/metrics.json
```

One task executed. The state file is why: `success` is a fact about a logical date and a task, not about a process that happened to finish.

The correctness of this depends on three assumptions, each worth writing down:

1. `train`'s output is still on disk and still valid for 2026-09-30.
2. `evaluate` is idempotent: re-running it overwrites `metrics.json` rather than appending.
3. Nothing outside the DAG changed between the two attempts (a dependency upgrade, a different data file).

If (3) is false, "resume" can produce a run whose tasks were computed with different environments. Production orchestrators record the image or environment per attempt for exactly this reason.

## What the four runs demonstrate

| Property | Evidence |
|---|---|
| Dependencies block work | `evaluate` never started while `train` was failing |
| Transient failures recover | `train` attempt 2 succeeded after a 1.0 s backoff |
| Permanent failures stop the run | `evaluate` exhausted 2 attempts, exit `1` |
| Failed work is not published | No `metrics.json` for 2026-09-30 until `evaluate` succeeded |
| Runs are idempotent | Re-running 2026-09-29 did nothing |
| Resume is real | Re-running 2026-09-30 executed only `evaluate` |
| State is inspectable | `--status DATE` prints attempts, durations, and errors |

## What a platform would add

The same DAG in Airflow or Prefect would add a UI, a database of historical runs, distributed workers, authentication, alerts, and backfill over a date range. It would also add a scheduler process and a metadata database to operate.

The reference implementation is enough to answer the question this module poses: *do you need that?* If your pipeline is one DAG, five tasks, one machine, and one owner, this is sufficient and you can read all of it. If you need seven days backfilled across three environments with an on-call rotation, the 120 lines become the platform you would have to build anyway — and then the platform's cost is easier to justify, because you have measured it.

## A note on the injection

`--inject` exists only to make failure reproducible in a course. Production failures are not scheduled; the equivalent is a task that raises `Transient` based on a real condition (timeout, HTTP 503, lock contention) and a task that raises a permanent error for everything else. The distinction lives in the code, not in a flag.

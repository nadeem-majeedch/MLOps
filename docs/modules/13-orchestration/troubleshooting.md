# Troubleshooting · Module 13

## Diagnose in this order

1. **Which logical date?** A run is identified by date, not by "last night".
2. **Which task?** Read the state file or UI before the logs.
3. **Did it retry?** Attempt count and last error separate a transient blip from a deterministic bug.
4. **Is it safe to re-run?** Check idempotency of the failed task before retrying it.
5. **Who is downstream?** A failed run may leave consumers reading yesterday's outputs without knowing.

## Failure table

| Symptom | Likely cause | Fix |
|---|---|---|
| Run never starts | Scheduler not running, timezone wrong, or a missed schedule | Check the scheduler process and the schedule's timezone |
| Run starts twice | No `max_active_runs` / lock, or two schedulers | Serialise runs per logical date |
| Resume reruns everything | State not persisted per task | Save state after each success |
| Duplicate rows or files | Non-idempotent task retried | Key on the logical date; write then replace |
| Retry storm | No backoff or no jitter | Exponential backoff with jitter, plus a cap |
| Run hangs forever | No task timeout | Per-task `timeout_s`; fail and retry |
| `metrics.json` from yesterday | Downstream reads a fixed path, not the date's output | Publish per-date paths and update a pointer only on success |
| Alerts ignored | Alerting on every retry | Alert on exhaustion, SLA breach, and missing runs |
| Backfill overwrites current data | Outputs not isolated by date | `runs/<date>/...`; never a single mutable file |

## Case 1: "it ran last night but the numbers are from last week"

Check three files in order:

```powershell
python orchestration/scheduler.py --status 2026-09-30
Get-Item runs/2026-09-30/metrics.json | Select-Object LastWriteTime
Get-Content metrics.json | Select-Object -First 5
```

If the state says success but the output is old, the task wrote elsewhere or the publishing step was skipped. This is the exact failure the module's state-plus-output check is designed to prevent: both must agree.

## Case 2: retries make it worse

A deterministic failure with a retry policy turns one error into three, and delays the alert that would have started the fix. Symptoms: identical error text on every attempt; duration grows linearly; downstream never starts.

The fix is classification, not fewer retries:

```python
try:
    run()
except (TimeoutError, ConnectionError) as exc:
    raise Transient(str(exc)) from exc       # retryable
except (KeyError, ValueError, SchemaError):
    raise                                 # permanent; fail now
```

## Case 3: backfill produces different numbers than the original run

Three usual causes:

1. **Wall-clock logic** inside a task (`now()`, `today()`, rolling windows computed from the clock).
2. **Mutable reference data** (a zone table, a holiday calendar) that changed since.
3. **Different environment** (package upgrade, model artifact replaced).

A backfill should reproduce history as it was, or explicitly declare that it recomputes with today's reference data. Either is defensible; discovering which one happened during an audit is not.

## Case 4: overlapping runs

If the interval is shorter than the runtime, runs pile up. Options:

- prevent (`max_active_runs: 1`, or a per-date lock);
- queue (a pool with one slot);
- allow, and make every task idempotent and the outputs date-scoped.

Allowing overlap without idempotency is how a pipeline corrupts its own outputs at 3 a.m.

## Case 5: the scheduler itself is the failure

Symptoms: no runs at all, runs for all missed dates at once when it restarts, or duplicate runs because two scheduler instances were started.

- Keep the scheduler's own logs and heartbeat separate from task logs.
- Decide catch-up explicitly; "run everything we missed" can be catastrophic after a week offline.
- Run exactly one scheduler instance; use the platform's HA mode rather than two crons.

## When to stop debugging the scheduler

If the DAG definition and the state are consistent, and a single task fails reproducibly outside the scheduler, the problem is in the task, not the orchestration. Run the task manually with the same logical date and environment; fix it there; then re-run the date. Editing the scheduler to work around a task bug is how DAGs acquire special cases nobody can remove.

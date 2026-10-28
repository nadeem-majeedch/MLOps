# Guided lab · A nightly run that survives a bad night

**Time:** 4 hours. **Tools:** Python 3.11/3.12, the pipeline from Module 08, Git. No scheduler service, no cloud account, no Kubernetes.

## Scenario and business problem

RaviRide retrains nightly at 02:00 on the previous day's trips. For three weeks the job was a cron entry running a shell script. Then a transient database timeout caused a partial run: features were rebuilt, training failed, and the old model kept serving while `metrics.json` claimed a fresh evaluation. Nobody noticed for two days because the only signal was a line in a log file.

You will build the smallest thing that fixes this: a dependency-aware run with retries, recorded state, idempotent re-runs, and a resume that executes only what is missing. Then you will decide — in writing — whether your team needs a platform instead.

### Skills practised

- Modelling work as tasks with explicit dependencies.
- Choosing retry policies per task and explaining the classification.
- Recording run state so a partial failure is recoverable.
- Making a run idempotent by keying it to a logical date.
- Resuming without recomputing or duplicating.
- Justifying (or rejecting) an orchestration platform with evidence.

### Prerequisites

- Module 08 complete: the four pipeline stages run from one command.
- Module 12 is helpful but not required: the same gate script is reused.
- A writable project directory; about 200 MB free.

### Input data

`data/raw/trips.csv` (1,200 rows) and the generated feature files. Each logical date uses the same dataset in this exercise; in production each date would select its own partition, which is why the logical date is part of the output path.

### Directory layout

```text
raviride-eta/
├── orchestration/scheduler.py
├── .orchestrator/<date>.json      # run state, ignored by Git
├── runs/<date>/metrics.json       # published output, ignored by Git
└── docs/orchestration-evidence.md
```

## Part 1: read the graph before running it (30 minutes)

1. Draw the DAG: five tasks, their dependencies, and the outputs each produces.
2. Write a prediction in `docs/orchestration-evidence.md`: if `train` fails once and then succeeds, which tasks run how many times?
3. Run the happy path:
   ```powershell
   python orchestration/scheduler.py --date 2026-09-29
   ```
   **Checkpoint 1:** five `success` lines, exit `0`, and `runs/2026-09-29/metrics.json` exists. Compare the attempt counts with your prediction.

## Part 2: transient versus permanent (45 minutes)

4. Make `train` fail once:
   ```powershell
   python orchestration/scheduler.py --date 2026-09-30 --inject train --inject-times 1
   ```
   **Checkpoint 2:** `train` shows attempt 1 failed and attempt 2 succeeded; the delay is printed. No other task is repeated.

5. Make `evaluate` fail more times than its retry budget:
   ```powershell
   python orchestration/scheduler.py --date 2026-10-01 --inject evaluate --inject-times 5
   ```
   **Checkpoint 3:** exit code `1`, `FAILED after 2 attempts`, and **no** `runs/2026-10-01/metrics.json`.

6. Inspect the state:
   ```powershell
   python orchestration/scheduler.py --status 2026-10-01
   ```
   **Checkpoint 4:** every earlier task is `success` with its duration; `evaluate` is `failed` with `last_error` and `attempts: 2`.

7. Answer in the evidence file: why is retrying `validate` zero times the right policy, and what would change your mind?

## Part 3: resume and idempotency (45 minutes)

8. Re-run the failed date:
   ```powershell
   python orchestration/scheduler.py --date 2026-10-01
   ```
   **Checkpoint 5:** only `evaluate` executes, and the run completes.

9. Re-run a completed date:
   ```powershell
   python orchestration/scheduler.py --date 2026-09-29
   ```
   **Checkpoint 6:** the scheduler reports the run is already complete and does nothing. Confirm the output file's modification time did not change.

10. Delete `runs/2026-09-29/metrics.json` and re-run. Explain why the result differs from step 9, and whether that behaviour is what you want.

## Part 4: make it safe under repetition (45 minutes)

11. Add a timeout to each task (a per-task `timeout_s`, enforced with `subprocess.run(..., timeout=...)`). Demonstrate it with a deliberately slow task.
12. Add jitter to the backoff (`delay = base * 2**(attempt-1) * random.uniform(0.8, 1.2)`) and record two retry delays to show they differ.
13. Make one task non-idempotent on purpose: append a line to `runs/<date>/predictions.jsonl` instead of overwriting it. Re-run the completed date after deleting its state file and count the duplicate lines. Then fix it with an idempotency key (for example, skip if the file already contains the run date).
    **Checkpoint 7:** you have produced a duplicate and then prevented it; the evidence file explains the mechanism.

## Part 5: backfill (30 minutes)

14. Run three consecutive logical dates in a loop:
    ```powershell
    foreach ($d in "2026-10-02","2026-10-03","2026-10-04") { python orchestration/scheduler.py --date $d }
    ```
15. Re-run the loop and confirm every date is skipped.
    **Checkpoint 8:** no duplicate outputs, and each date has its own state and metrics file.

## Part 6: the decision memo (25 minutes)

16. Write `docs/orchestration-evidence.md` with:
    - the DAG and the retry policy table, with a reason per task;
    - the four run logs (happy, retry, exhaustion, resume);
    - the measured durations;
    - a decision: script, this scheduler, or a platform — with three criteria and the cost you are accepting;
    - the three things that would force a change (for example: multiple owners, backfills beyond a week, tasks needing different machines).
17. Commit the scheduler and the evidence file. Do not commit `.orchestrator/` or `runs/`.

## Expected outputs

| Output | Reference value |
|---|---|
| Happy run | 5 successes; validate 0.55 s, prepare 0.53 s, featurise 0.55 s, train 2.29 s (after retry), evaluate 1.54 s |
| Transient retry | attempt 1 failed, retried in 1.0 s, attempt 2 succeeded |
| Exhausted retries | `FAILED after 2 attempts`, exit `1`, no metrics file |
| Idempotent re-run | `run already complete ... nothing to do` |
| Resume | four tasks `already succeeded, skipping`; only `evaluate` runs |
| State | one JSON per date with attempts, durations, errors |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Graph | Dependencies are explicit and a failed parent blocks children |
| Retry policy | Per-task, justified, with backoff and jitter |
| State | A partial failure is recoverable from the state file alone |
| Idempotency | Completed dates do nothing; failed dates resume |
| Isolation | Each logical date writes to its own paths |
| Evidence | Four real run logs, durations, and a decision memo |
| Honesty | The memo names what the implementation cannot do |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| All tasks rerun on resume | State not saved after each success | Save state immediately after a task succeeds |
| `metrics.json` missing after success | Output copy happens only at the end; a later task failed | Expected; rerun the failed tail |
| Duplicate rows after retry | Task appends instead of overwriting | Write to a temp file and replace, or key on the run date |
| Retries happen instantly | Backoff not applied | Sleep between attempts; add jitter |
| Run date changes between attempts | Using `now()` inside a task | Pass the logical date through |
| Two runs of the same date overlap | No lock or state check | Check state before starting; add a per-date lock |

## Cleanup

```powershell
Remove-Item -Recurse -Force .orchestrator, runs -ErrorAction SilentlyContinue
```

Keep the scheduler and the evidence file. No services were started, so nothing needs stopping.

## Optional extensions

1. **Concurrency limit.** Run two dates in parallel with a cap of one task of each type at a time. Explain which shared resource (the model file, the metrics file) forces the limit.
2. **Alerting.** Send a desktop notification or write to a `alerts.log` on exhaustion, and a separate line on SLA breach (run not finished within N seconds). Explain why alerting on every retry is wrong.
3. **Port to Prefect or Airflow.** Rewrite the same five tasks in one of them, locally, and record what you gained, what you lost, and how long the setup took. This is the evidence most teams never collect before choosing.

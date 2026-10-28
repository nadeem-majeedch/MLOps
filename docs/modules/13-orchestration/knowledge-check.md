# Knowledge check · Module 13

## Questions

**1.** A nightly job starts at 02:00 on 30 September and processes the previous day's trips. What is its logical date, and why does the distinction matter for a re-run?

**2.** Name three capabilities a cron entry does not provide that a pipeline eventually needs.

**3.** A task that appends one row to a table per run is retried after a timeout. What is the likely state of the table, and what property should the task have had?

**4.** Why does exponential backoff without jitter cause problems when a shared dependency fails?

**5.** `validate` has zero retries and `train` has two. Justify both choices in one sentence each.

**6.** After a failure in `evaluate`, the next run executes only `evaluate`. Name two assumptions that must hold for that to be correct.

**7.** What is the difference between catch-up and backfill?

**8.** A pipeline is scheduled every 10 minutes and takes 15 minutes. What will happen, and what setting or property prevents the worst outcome?

**9.** Why is `datetime.now()` inside a task a bug in a scheduled pipeline?

**10.** Your team runs one five-task DAG on one machine, owned by two people, with no need for backfills. Give the argument for not installing Airflow, and the signal that would change the decision.

---

## Answers and reasoning

**1.** The logical date is `2026-09-29`: the date the run represents. Re-running "2026-09-29" is unambiguous and selects the same inputs; re-running "yesterday" changes meaning depending on when you type it, and a backfill cannot express it at all.

**2.** Any three of: dependencies between steps with per-step status; retries with recorded attempts; resume after partial failure; backfill over past dates; visibility and alerting; isolation between tasks. Cron gives a trigger and nothing else.

**3.** Duplicate rows, one per attempt (and possibly a partial row if the timeout interrupted a write). The task needed **idempotency**: an upsert keyed by a natural key, or a write to a temporary location followed by a replace. At-least-once execution makes idempotency a requirement, not a refinement.

**4.** Every task that failed at the same moment retries at the same moment, so the recovering dependency receives a synchronized burst instead of a gradual load. Jitter spreads the retries; a cap prevents an unbounded herd.

**5.** `validate` re-reads a deterministic file: if it fails, the data is wrong and retrying produces the same error with more noise. `train` can fail for transient reasons (memory pressure, a temporary dependency) where a second attempt is likely to succeed and the cost of trying is a few seconds.

**6.** That `train`'s output is still present and still valid for that logical date, and that `evaluate` is idempotent (re-running overwrites rather than appends or double-counts). A third, often forgotten: the environment has not changed between attempts.

**7.** **Catch-up** is the scheduler automatically running dates it missed while it was down or behind. **Backfill** is a deliberate request to process a range of past dates, usually after a bug fix or a new feature. Catch-up is a scheduling policy; backfill is an operation a human initiates.

**8.** Runs overlap: the next starts before the previous finishes, so two runs of the same (or adjacent) logical dates compete for the same files and resources. Prevention: `max_active_runs: 1` (or a per-date lock), plus either a longer interval or a faster pipeline. Idempotency makes overlap survivable but does not make it efficient.

**9.** Because a re-run or backfill then produces a different result from the original run for the same logical date, and the difference is invisible in the output. Time-dependent values must come from the logical date or from data, not from the clock.

**10.** The argument: the platform adds a scheduler, a metadata database, a UI to secure, upgrades, and an on-call surface, for a workload one person can reason about and restart by hand. The signal to change: a second team needs to schedule work, backfills become routine, runs must survive the machine being rebuilt, or failures need alerting and an audit trail that a JSON file cannot provide.

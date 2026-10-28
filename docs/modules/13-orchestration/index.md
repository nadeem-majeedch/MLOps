# 13 · Workflow orchestration

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 14 hours | [08](../08-pipeline-automation/index.md), [12](../12-ci-cd/index.md) | Recommended |

CI answers "is this change sound?". Orchestration answers a different question: "run this at 02:00 every day, in the right order, retry the parts that fail, tell someone when it breaks, and let me re-run last Tuesday".

Those are not the same problem, and the tools are not interchangeable. A cron entry is an orchestrator for one job; Airflow is an orchestrator for hundreds with dependencies and backfills. Between them is a large space where most teams live, and choosing the wrong point in that space is expensive in both directions.

## What you will be able to do

- Decide whether a script, a cron entry, or an orchestration platform is justified.
- Explain logical run dates, task instances, retries, backoff, and idempotency.
- Read a run's state and say which tasks succeeded, retried, or were blocked.
- Design a retry policy that distinguishes transient from permanent failures.
- Resume a partially failed run without recomputing everything or duplicating outputs.
- Compare Airflow, Prefect, Dagster, Argo Workflows, and a plain scheduler on criteria that matter to a small team.

## Start here

1. Read [Concepts](concepts.md) sections 1–7: when to orchestrate, run dates, retries, idempotency.
2. Read the [worked example](worked-example.md): a 120-line scheduler, a transient failure that recovered, and a hard failure that resumed correctly.
3. Do the [lab](lab.md): add a retry policy, exhaust it, and resume without duplicating work.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the orchestration-review criteria |
| [Concepts](concepts.md) | Scheduling, DAGs, run dates, retries, idempotency, tool comparison |
| [Worked example](worked-example.md) | Real runs: retry, exhaustion, idempotent re-run, resume |
| [Guided lab](lab.md) | Build and break a small scheduler |
| [Independent challenge](independent-challenge.md) | Backfill seven days without duplicating a single output |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Stuck runs, retry storms, duplicate outputs, missed schedules |
| [References](references.md) | Airflow, Prefect, Dagster, Argo, and scheduling fundamentals |

## What you produce

- A runnable dependency-aware workflow with retries and recorded state.
- A transient failure that succeeds after a retry, with attempt numbers.
- A hard failure that stops the run and leaves earlier tasks reusable.
- A resumed run that executes only the missing work.
- A written decision: script, cron, or platform, with the criteria you used.

## The reference run

`orchestration/scheduler.py` runs the RaviRide pipeline as five tasks with declared dependencies. On the reference machine, `validate`–`featurise` take about 0.55 s each, `train` about 2.0 s, and `evaluate` about 1.5 s. A simulated transient failure in `train` was retried after 1.0 s and succeeded on attempt 2 (2.29 s); a simulated permanent failure in `evaluate` exhausted two attempts and exited `1`; re-running the same logical date executed only `evaluate`. All numbers are local; the state machine is the transferable part.

## Next

[Module 14](../14-monitoring-drift/index.md) watches what these runs produce: prediction logs, drift, and the decision to retrain.

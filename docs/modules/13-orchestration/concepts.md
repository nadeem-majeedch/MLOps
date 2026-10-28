# Concepts · Running things on a schedule without losing your mind

## 1. What orchestration actually buys

A scheduled pipeline needs more than a timer. The capabilities that matter, in the order they start to hurt:

1. **Scheduling without a person.** Trigger at a time, or when data arrives.
2. **Dependencies.** `evaluate` runs only after `train`, and a failed parent blocks children.
3. **Retries with state.** A transient network failure should not require a full re-run, and the retry should be recorded.
4. **Resume.** After a failure at task 4, the next attempt starts at task 4, not task 1.
5. **Backfill.** "Re-run the pipeline for every day last month."
6. **Visibility.** What ran, when, how long, how often it failed, who was paged.
7. **Isolation.** Tasks that cannot interfere with each other's resources or secrets.

A `cron` entry gives you (1) and nothing else. A script with `&&` gives you (2) in the trivial sense that it stops at the first failure, but no retry and no resume. The reference scheduler in this module implements (1)–(5) and a little of (6) in about 120 lines. Everything above that is what platforms sell.

## 2. When a script is enough

Most pipelines do not need Airflow. A script is sufficient when:

- it runs on one machine, triggered by one schedule or one person;
- a failure means "run it again", and running it again from the start is acceptable;
- there is no need to re-run arbitrary past dates;
- one person owns it and reads the logs when it breaks.

A decision ladder, cheapest first:

| Need | Tool |
|---|---|
| Run at a time, one step, manual recovery | `cron` / Task Scheduler / `systemd` timer + a script |
| Several steps, order matters, no retries needed | one script with `&&` and `set -e` |
| Retries, resume, run state, a few dependencies | the small scheduler in this module |
| Many DAGs, backfills, a UI, several owners | Airflow / Prefect / Dagster |
| Kubernetes already, container-per-step | Argo Workflows |
| Long-running business processes with external events | Temporal |

The cost of a platform is not the licence (most are open source). It is the scheduler process, the metadata database, upgrades, the UI's authentication, the on-call rotation that now includes the orchestrator, and the YAML or Python that someone must learn. For a team of two running one pipeline, that cost is real.

The cost of *not* adopting one appears later: a pile of scripts with hand-rolled locking, no run history, and a wiki page explaining which order to run them in. The decision is about which cost you are better placed to pay, now and in a year.

## 3. Vocabulary that stops arguments

| Term | Meaning |
|---|---|
| **DAG** | Directed acyclic graph of tasks; the workflow definition |
| **Task** | One unit of work with inputs, outputs, and a retry policy |
| **Run** | One execution of the DAG, identified by a logical date |
| **Logical date** | The date the run *represents*, not the time it started |
| **Task instance** | One task within one run; the unit that succeeds or fails |
| **Backfill** | Running the DAG for past logical dates |
| **Catchup** | Whether the scheduler automatically runs missed dates |
| **Sensor** | A task that waits for a condition (a file, an upstream table) |
| **SLA** | A deadline by which a run should complete; alerting, not enforcement |
| **Pool / concurrency limit** | A cap on how many tasks of a kind run at once |

## 4. The logical date is the spine

A daily pipeline at 02:00 on 30 September processes **29 September's** data. Its logical date is `2026-09-29`, even though it ran on the 30th.

Why this matters:

- **Re-runs.** "Run 2026-09-29 again" is unambiguous. "Run yesterday" is not, especially at 23:59.
- **Backfills.** Filling January means running logical dates 2026-01-01 through 2026-01-31, each with the data that existed for that day.
- **Idempotency.** Output paths keyed by logical date (`runs/<date>/metrics.json`) cannot collide across days.
- **Late data.** If a source lands at 03:00 instead of 01:00, the run for the previous day is still the previous day's run.

The reference scheduler takes `--date` and uses it as the key for state and outputs:

```text
runs/2026-09-29/metrics.json
.orchestrator/2026-09-29.json
```

Running the same date twice is therefore safe by construction: the second run sees completed state and stops.

## 5. Execution semantics: at least once, so be idempotent

Almost every orchestrator guarantees **at-least-once** execution: a task may run more than once because of retries, worker crashes, or a scheduler restart. Exactly-once is a property you build, not one you configure.

Consequences:

- A task that appends a row per run will duplicate rows on retry.
- A task that overwrites a file by logical date is naturally idempotent.
- A task that calls an external API with side effects (sending an email, charging a card) needs an idempotency key.

The reference tasks are idempotent because each one overwrites its outputs from its inputs. The state file makes the *run* idempotent as well: a completed date does no work.

## 6. Retries: helpful, dangerous, and often misunderstood

A retry policy has four parts:

1. **Classification.** Which failures are transient? Network timeouts, rate limits, a locked file, a temporarily unavailable database. Which are permanent? A schema error, a missing column, a unit test failure, a bug.
2. **Count.** How many attempts before giving up. Two or three is typical for transient infrastructure; zero for deterministic code errors.
3. **Backoff.** Delay between attempts, usually exponential: 1 s, 2 s, 4 s… Immediate retries amplify load exactly when a dependency is struggling.
4. **Jitter.** Randomness added to the delay so many tasks that failed together do not retry together.

Retrying a deterministic failure is pure cost: the same input produces the same exception, three times, with a longer incident. The reference scheduler separates the two by task:

| Task | Retries | Reason |
|---|---|---|
| `validate` | 0 | A schema failure is a data defect; retrying re-reads the same bad file |
| `prepare` | 1 | File contention or a transient read error is plausible |
| `featurise` | 1 | Same |
| `train` | 2 | Memory pressure or a transient dependency failure |
| `evaluate` | 1 | Reads a local artifact; failures are usually permanent |

**Retry storms.** Without jitter and a cap, a shared dependency that fails causes every task to retry on the same schedule, doubling load at the worst moment. Backoff without jitter is better than nothing; backoff with jitter is the default you want.

**Poison tasks.** A task that fails deterministically will exhaust its retries on every run, producing noise and cost until someone fixes it. Alert on repeated exhaustion, not just on a single failure.

## 7. Partial failure and resume

The most useful property of an orchestrator is not that it retries; it is that it knows what already succeeded.

Reference run on `2026-09-30` with a permanently failing `evaluate`:

```text
validate: success
prepare: success
featurise: success
train: success
evaluate: FAILED after 2 attempts
```

Re-running the same date:

```text
validate: already succeeded, skipping
prepare: already succeeded, skipping
featurise: already succeeded, skipping
train: already succeeded, skipping
evaluate: success on attempt 1 in 1.54s
```

Two things had to be true for that to be correct:

- the earlier tasks' outputs were still valid for that logical date;
- the failed task was idempotent, so running it again produced the same result rather than a duplicate.

If either is false, "resume" is a footgun. A task that appends to a table, or whose output depends on the wall clock, cannot be resumed safely without extra care.

## 8. Scheduling details that cause incidents

- **Timezone.** `0 2 * * *` in whose timezone? Store the schedule's timezone explicitly. A pipeline that shifts by an hour twice a year will eventually produce a duplicate or missing run.
- **DST.** On the day clocks move forward, 02:00 may not exist; on the day they move back, it occurs twice. Use a scheduler that handles this, and make runs idempotent so a duplicate is harmless.
- **Missed runs.** If the scheduler is down at 02:00, does it run when it comes back (catchup) or skip? Both are defensible; undocumented is not.
- **Overlap.** If a run takes longer than the interval, two runs of the same date may execute concurrently. Most schedulers have a `max_active_runs` setting; the reference scheduler's state check is the crude equivalent.
- **Clock skew.** Two machines disagreeing about "now" produce runs that appear to start before they were scheduled. The logical date sidesteps this; wall-clock logic does not.

## 9. Backfill is the feature that pays for the platform

Backfill means running a DAG for a range of past logical dates. It is needed when:

- a bug in feature code invalidated a month of training data;
- a new feature must be computed historically to train on it;
- a downstream consumer needs reprocessed outputs.

Doing this with scripts means a loop, a lock, a way to skip completed dates, and a way to stop halfway. That is an orchestrator's core competence. It also exposes every non-idempotent task at once, which is why backfills are both the best argument for orchestration and the best test of it.

## 10. Visibility and alerting

A run's state should answer, without reading logs:

- which logical dates ran, and which are missing;
- which tasks failed, how many attempts, and the last error;
- how long each task took, compared with yesterday;
- whether a run is still going or stuck.

Alert on:

- a failed run (after retries are exhausted);
- a run that has not finished by its SLA;
- a task that has retried more than N times across runs (a slow leak);
- a gap in run dates (the scheduler itself is down).

Alerting on every retry trains people to ignore alerts. Alert on exhaustion and on absence.

## 11. Comparing the tools honestly

| Tool | Model | Strengths | Costs | Fits when |
|---|---|---|---|---|
| **cron / systemd / Task Scheduler** | One command per entry | Zero dependencies, already installed | No dependencies, no state, no retries, no history | One job, one machine, manual recovery |
| **This module's scheduler** | Python tasks + JSON state | Readable, no services, teaches the concepts | Single machine, no UI, no distributed workers | Small team, few DAGs, one host |
| **Apache Airflow** | Python DAGs, scheduler + metadata DB + web UI | Mature, huge ecosystem, backfill and catch-up, managed options | Operationally heavy; DAG scheduling is not the same as dataflow; upgrades hurt | Many DAGs, several teams, existing platform staff |
| **Prefect** | Python functions with decorators | Low ceremony, dynamic workflows, good local experience | Server/Cloud for coordination; fewer built-in data-asset semantics | Python-first teams wanting less infrastructure than Airflow |
| **Dagster** | Software-defined assets | Asset lineage, typed I/O, strong local dev | New mental model; platform overhead grows with scale | Teams thinking in datasets and lineage |
| **Argo Workflows** | YAML, container per step, Kubernetes | Native to Kubernetes, isolated steps | Needs a cluster; YAML for complex logic is painful | Already on Kubernetes, containerised steps |
| **Kubeflow Pipelines** | Python DSL compiled to Argo | ML-specific components, UI | Heavy; cluster required; upgrade churn | Platform teams running many ML pipelines on K8s |
| **Temporal** | Durable code execution | Retries, timers, long-running workflows, strong consistency | Different problem shape; not a data scheduler | Business processes with external events |
| **Cloud schedulers** (EventBridge, Cloud Scheduler, Step Functions) | Managed triggers/state machines | No servers, IAM integration | Vendor lock-in, per-transition cost, limited local dev | Cloud-native, simple graphs |

Two honest notes:

- **Airflow is not a data-processing engine.** Tasks should hand off to something else (a Spark job, a container, a script). Doing heavy compute inside the scheduler's worker is a common and painful mistake.
- **GitHub Actions `schedule` is not an orchestrator.** It can run a cron workflow, but it has no backfill, no task-level resume, and no run state beyond workflow runs; scheduled workflows in inactive repositories are also disabled after a period. Fine for a nightly smoke test, wrong for a production data pipeline.

## 12. Anti-patterns

| Anti-pattern | Why it hurts |
|---|---|
| One giant task | No resume, no partial retry, no visibility |
| Hidden state between tasks (a file in `/tmp`, a global) | Works on one worker, fails on another; breaks backfill |
| Retries on deterministic errors | Triples the cost of every bug and delays the alert |
| No timeout | A hung task blocks the run and the next one |
| Schedule density without concurrency limits | Ten runs overlap and exhaust the database |
| Wall-clock logic inside tasks | Backfills produce today's answer for last month's date |
| Alerts on every retry | The channel is muted within a week |
| Orchestrator as compute | The scheduler becomes the bottleneck and the single point of failure |

## 13. What the reference scheduler is not

It has no daemon, no UI, no distributed workers, no authentication, and no persistence beyond a JSON file on one disk. It does not survive the machine being rebuilt. It is a teaching implementation of the concepts, and the lab asks you to extend it until its limits are obvious — which is the point at which a platform starts to be worth its cost.

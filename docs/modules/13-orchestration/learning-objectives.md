# Learning objectives · Module 13

| # | Objective | Evidence |
|---|---|---|
| 1 | Justify orchestration or reject it | A written decision with three criteria and the cost of the alternative |
| 2 | Model a workflow as a DAG with explicit dependencies | A task table: name, dependencies, retries, timeout |
| 3 | Use a logical run date, not the wall clock | A run keyed by date, re-runnable months later |
| 4 | Separate transient from permanent failures | A retry policy with a stated rule per task |
| 5 | Implement backoff and explain jitter | A retry log with attempt numbers and delays |
| 6 | Make tasks idempotent | A re-run that produces no duplicate output |
| 7 | Resume a partial run | A resumed run that executes only the failed and downstream tasks |
| 8 | Read run state | A state file or UI that answers what ran, when, and how often |

## Orchestration review criteria

A workflow is reviewable when an on-call engineer can answer these at 3 a.m. without reading the code:

- [ ] What is the schedule, in which timezone, and what happens on a missed run?
- [ ] What are the tasks and their dependencies? Can the graph be drawn?
- [ ] Which tasks are safe to retry, and which would duplicate an effect if retried?
- [ ] What is the timeout per task, and what happens when it is exceeded?
- [ ] Where is run state stored, and how long is it kept?
- [ ] How does a failed run alert a human, and who is that human?
- [ ] How do you re-run one date without touching the others?
- [ ] What happens when two runs of the same date overlap?

## The test for "do we need this?"

Ask three questions:

1. **Does it need to run without a person?** If a human presses the button, a script is enough.
2. **Are there dependencies between steps that can fail independently?** If one command does everything and either works or does not, a script with a retry is enough.
3. **Will you need to re-run a specific past date, or run many dates at once?** Backfill is where scripts become unmaintainable and platforms earn their cost.

Two yeses justify looking at a platform. Three yeses, with a team that will operate it, justify adopting one.

## Self-check before you start

You should have a pipeline that runs from one command (Module 08) and a CI workflow (Module 12). You do not need prior Airflow experience; the module teaches the concepts with a small implementation first.

After the module, you can answer:

1. Why is "the run date" not the same as "now"?
2. What makes a retry safe, and which tasks are unsafe to retry?
3. Why can adding retries make an incident worse?
4. What does a scheduler guarantee about execution — once, at least once, or at most once?
5. What would you have to add to a cron entry before it is a trustworthy daily pipeline?

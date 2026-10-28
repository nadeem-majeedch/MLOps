# Independent challenge · Backfill seven days without duplicating a single output

## The brief

A feature bug invalidated a week of training data. Rebuild the outputs for seven consecutive logical dates, with these constraints:

- a mid-backfill failure must not require starting over;
- running the backfill twice must produce exactly the same set of outputs;
- no date may be silently skipped;
- the whole thing must finish unattended and leave evidence.

Then write a one-page decision: would you run this backfill with your scheduler, or would you install a platform first? Defend it with the numbers you measured, not with preference.

## Requirements

1. **A date range argument**, for example `--from 2026-09-22 --to 2026-09-28`, processed in order.
2. **Per-date isolation**: state and outputs keyed by the logical date, never overwritten by a neighbouring date.
3. **Resume**: stop the backfill mid-way (inject a failure on day 4), fix the cause, and continue without recomputing days 1–3.
4. **No duplicates**: after two full iterations of the range, every output file exists once and its content is unchanged.
5. **A summary**: dates processed, dates skipped, failures, total wall time, and the slowest date.
6. **Evidence of a skipped date**: deliberately remove one date's state and output, re-run the range, and show that only that date is recomputed.

## What to submit

- The backfill command and its output for the full range.
- The interrupted run: the failure, the state before and after, and the resume.
- A duplicate check: a script or command that proves each date has exactly one metrics file and that its hash did not change on the second pass.
- The timing table.
- The decision memo.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Completeness | Seven dates, each with state and output |
| Isolation | No date's output contains another date's data or a wall-clock value |
| Resume | A mid-range failure costs only the failed date onward |
| Idempotency | Second pass changes nothing; hashes identical |
| Detectability | A missing date is noticed, not skipped silently |
| Decision | The memo uses the measured wall time and failure behaviour |

## Questions to answer

1. What was the total wall time, and what would it be if every date re-ran from scratch?
2. If the pipeline took 40 minutes per date instead of 5 seconds, what would change about your tooling choice?
3. What happens if two backfills of overlapping ranges run at once? Does your implementation prevent it, detect it, or ignore it?
4. Which task was least safe to retry, and why?

## Stretch

Add a **catch-up mode**: given a start date and "today", process only the dates with no successful run, in order, with a maximum of one concurrent run. Then explain how your implementation handles a date that is still running when the next one becomes due.

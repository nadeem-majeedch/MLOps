# Answer key · Question bank 06

[Back to the questions](../../question-bank/06-cicd-orchestration.md)

---

## Section A (1 mark each)

**A1 — b.** Explicit least privilege. `write-all` (a) is the opposite; relying on
unspecified defaults (c) is how a repository becomes writable after a settings
change.

**A2 — b.** A logged token is compromised the moment it is stored, even if the job
is private. Revoke first, then remove, then prevent. Rotation alone (c) leaves the
exposure in history.

**A3 — a.** Idempotence: running twice leaves the same state. A random suffix (c)
creates duplicates; a longer timeout (b) only postpones the retry.

**A4 — b.** The criterion is structure and visibility, not tool fashion. A single
process with no dependencies and a failure someone sees needs no orchestrator;
several dependent tasks with retries and history do.

## Section B (3 marks each)

**B1.** A warning is ignorable, and the build's green tick becomes evidence it is
not. The failure mode: the gate runs for months, everyone learns it is advisory,
and a real regression ships with a warning nobody read. If a check is not worth
failing on, delete it; a permanently yellow signal trains people to ignore yellow.

**B2.** A retry re-runs the same logical interval after a transient failure; it
must be idempotent and bounded. A backfill re-processes historical intervals that
were missed or wrong, often with a fixed code version. Retry a timeout; backfill a
wrong partition or an outage that skipped a day.

**B3.** Artifacts: test reports, coverage, metric JSON, a small validation report,
and (short retention) the built image digest or SBOM. Never: credentials, `.env`
files, raw personal data, full datasets, model binaries with proprietary weights,
or source maps containing internal paths — unless the storage and access are
designed for them.

## Section C (4 marks each)

**C1.** Gaps:

| Gap | Step that closes it |
|---|---|
| No test of the built image | Start the container and hit `/health` and `/predict` |
| No data validation | Schema and null checks on the actual input before training |
| No gate on model quality | Metric floor against a pinned baseline |
| No migration or config check | Apply migrations and validate env vars in a staging run |

Accept any three. One mark for the gap, one for the step that would have caught
the specific failure.

**C2.** Causes: outputs include a timestamp or run ID; a task reads `now()` and
its output depends on it; upstream input is re-uploaded with a new name each
night; the orchestrator's cache is disabled or the working directory is wiped;
a task declares no outputs, so the scheduler cannot know it is unchanged. One
check each: inspect declared outputs, diff the output paths between runs,
compare the upstream file hashes, and read the scheduler's skip log.

## Section D (9 marks)

| Element | Marks | What it looks like |
|---|---|---|
| Triggers | 1 | Weekly schedule, plus manual dispatch; pull-request CI for code changes |
| Automated gates | 2 | Data validation, tests, metric floor on a fixed holdout, slice checks, artifact build |
| Human approval | 2 | Promotion after the gates, with the evidence attached; a named approver and a rollback plan |
| Artifact and evidence retention | 2 | Model, metrics, data hash, and gate report kept for the audit window; reports uploaded, not only printed |
| Rollback | 1 | Alias repointed to the previous version, timed, with the trigger conditions written down |
| Separation of duties | 1 | CI can build and test; only a release workflow with the right environment protection can promote |

A strong answer says automated retraining may open a release candidate but should
not silently replace the champion, because a green gate is necessary and not
sufficient. Requiring approval for every model change and never automating the
gates both lose marks.

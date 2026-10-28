# Question bank 06 · CI/CD and orchestration

| | |
|---|---|
| **Covers** | [Module 12](../../modules/12-ci-cd/index.md), [Module 13](../../modules/13-orchestration/index.md) |
| **Level** | Advanced |
| **Questions** | 10 |
| **Marks** | 30 |
| **Time** | 45 minutes |
| **Answer key** | [06 · Answers](../solutions/question-bank/06-cicd-orchestration-answers.md) |

---

## Section A · Multiple choice (4 marks)

**A1.** A workflow needs to read repository contents and nothing else. Which
`permissions` block is correct?

- a) `permissions: write-all`
- b) `permissions: { contents: read }`
- c) No permissions block; defaults are read-only
- d) `permissions: { actions: write, contents: write }`

**A2.** A token is printed by a failing test. What is the correct response?

- a) Delete the log line and continue
- b) Revoke the token, remove it from history, and add a scan that prevents recurrence
- c) Re-run the job so the log is replaced
- d) Move the token to a repository variable

**A3.** A nightly pipeline task must be safe to retry after a timeout. What
property does it need?

- a) Idempotence
- b) A longer timeout
- c) A random suffix on its output table
- d) A manual approval step

**A4.** When is a single scheduled script sufficient, without an orchestrator?

- a) Never; orchestration is always better
- b) When the work is one process, has no cross-task dependencies, and its failure
  is visible
- c) When the team has no Kubernetes cluster
- d) When the pipeline runs less than once a day

---

## Section B · Short answer (9 marks)

**B1.** *(3 marks)* Why must a CI quality gate fail the build rather than post a
warning? Give the failure mode warnings produce.

**B2.** *(3 marks)* Explain the difference between a retry and a backfill, and
when each is appropriate.

**B3.** *(3 marks)* What belongs in a workflow artifact, and what must never be
uploaded? Name three of each.

---

## Section C · Debugging and diagnosis (8 marks)

**C1.** *(4 marks)* CI is green on every pull request, but the deployed service
is broken. The workflow runs lint, unit tests, and a container build. Name three
gaps and the step that would close each.

**C2.** *(4 marks)* A DAG reruns all upstream tasks every night even when their
inputs are unchanged. Give three causes and one check for each.

---

## Section D · Architecture and scenario (9 marks)

**D1.** Design the automated release process for a model that is retrained weekly.
Include triggers, gates, approvals, artifact retention, and rollback. State what
runs automatically and what requires a human, with a reason for each. *(9 marks)*

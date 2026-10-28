# Troubleshooting · Module 12

## Diagnose in this order

1. **Did the workflow run at all?** No run means a trigger or path-filter problem, not a failing step.
2. **Which job failed?** Read the first failing step, not the last log line.
3. **Does it fail locally?** Reproduce the command in the same environment before changing the workflow.
4. **What is different?** Python version, dependency versions, files present, environment variables, permissions.
5. **Is the gate failing for the right reason?** Print the baseline hash and the candidate's metric.

## Workflow does not run

| Symptom | Cause | Fix |
|---|---|---|
| No check appears on the PR | YAML syntax error, or the file is not on the branch | Validate with `check-jsonschema`; confirm the path |
| Runs on push but not on PR | Trigger missing, or the PR targets another branch | Add `pull_request`; check the base branch |
| Skipped because of path filters | Only unrelated files changed | Add the missing path, or use `workflow_dispatch` to test |
| Runs twice | Both `push` and `pull_request` fire for a branch in the same repo | Restrict `push` to `main` |
| Immediately cancelled | `concurrency` with `cancel-in-progress` and a newer commit | Expected; inspect the latest run |

## Job failures that pass locally

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError` | Dependency not in the requirements file | Install from the same files CI uses |
| Different test result | Python version differs | Match the matrix locally, or narrow the matrix |
| `FileNotFoundError` for data | Data is DVC-tracked and not pulled | Add `dvc pull` with credentials, or commit a small fixture |
| Gate passes locally, fails in CI | Baseline differs, or the workspace has uncommitted changes | Print the baseline hash and `git status` at the start of the gate |
| `Permission denied` writing a file | Working directory differs, or the path is absolute | Use repository-relative paths |
| Timeout | Slow installs, no cache, or the gate on every push | Cache dependencies; add `timeout-minutes`; restrict triggers |

## Secrets and permissions

| Symptom | Cause | Fix |
|---|---|---|
| `Resource not accessible by integration` | Token scope too narrow for the step | Add the specific permission to that job |
| `Bad credentials` when pushing | `contents: read`, or a fork PR | Grant `contents: write` only where needed; do not push from forks |
| Secret is empty | Not defined, or defined at environment level without the environment | Check repository/organisation/environment scope |
| Secret appears as `***` and breaks a command | Masking replaced a value you also needed to read | Use a non-secret test value; pass secrets via stdin |
| Fork PR cannot read secrets | By design | Do not run privileged steps on fork code; use `pull_request` |

## Cache problems

| Symptom | Cause | Fix |
|---|---|---|
| Install is fast but versions are wrong | Cache key does not include the requirements file | Ensure `cache: pip` with the right `cache-dependency-path` |
| Old `metrics.json` used by the gate | Metrics cached | Remove generated evidence from caches |
| Cache never hits | Key changes every run (timestamp, lockfile churn) | Key on the dependency files only |
| Disk full | Large caches or artifacts | Prune caches; reduce artifact size |

## The gate

```text
FAIL overall mae 3.4416 (baseline 2.7686, allowed 2.9070, tolerance 5%)
FAIL Z08 mae 7.3065 (baseline 5.5812, allowed 6.4184, tolerance 15%)
```

Read it in this order:

1. **Is the candidate metric plausible?** 3.44 against a usual 2.77 is a real degradation, not noise.
2. **Is the baseline the right one?** Check its hash and commit.
3. **Is the data the same?** A different split or a regenerated dataset changes the question, not just the answer.
4. **Is the tolerance appropriate?** Loosening it to pass is a decision that needs an owner, not a commit.

If the candidate metric is **better** and the gate still fails, a slice is worse. That is the gate doing its job, and the decision belongs to a human with the slice analysis in hand.

## When to stop debugging CI

If the same command produces the same result locally and in CI, CI is not the problem; the change is. If the result differs, stop changing the workflow and compare environments field by field: Python version, package lock, data hash, environment variables, working directory. Workflow edits made before that comparison tend to add variables rather than remove them.

# Guided lab · Make a worse model impossible to merge

**Time:** 5 hours. **Tools:** Git, a GitHub repository you can push branches to, GitHub Actions (free tier is enough), Python 3.11/3.12. Docker is optional and only used by the stretch task.

## Scenario and business problem

RaviRide's model changes arrive as pull requests. Reviewers look at the diff, run the tests if they remember, and occasionally ask for the MAE. Twice this quarter a model with a worse error in one zone reached `main`, because the overall number looked fine and nobody checked the slices.

You will make the checks part of the merge condition: lint and tests on every pull request, a pipeline and regression gate only when the model can change, and branch protection so a red check cannot be merged by enthusiasm.

### Skills practised

- Writing workflows with minimal triggers and least-privilege permissions.
- Separating fast feedback from expensive evidence.
- Uploading artifacts from failing runs.
- Turning a metric comparison into a required status check.
- Handling secrets without exposing them.
- Explaining what the green check does not prove.

### Prerequisites

- Modules 07, 09, and 11 complete: tests, a model gate script, and a Dockerfile.
- A GitHub account and a repository containing this project.
- Push access to a branch; permission to configure branch protection (or a personal repository, where you are the admin).

### Input data

The repository itself: `data/raw/trips.csv` (or the DVC pointer), `baseline.json`, `metrics.json`, and `params.yaml`. No external data is downloaded during the lab.

### Directory layout

```text
raviride-eta/
├── .github/workflows/
│   ├── ci.yml
│   └── model-validation.yml
├── scripts/check_metrics.py
├── baseline.json
└── src/, serving/, tests/
```

## Part 1: the fast workflow (60 minutes)

1. Create `ci.yml` with `pull_request`, `push` to `main`, and `workflow_dispatch` triggers.
2. Add `permissions: contents: read` and a `concurrency` group with `cancel-in-progress: true`.
3. Add a `lint` job that installs `ruff` and runs it on the code directories.
4. Add a `test` job with a matrix over Python 3.11 and 3.12, `fail-fast: false`, and a JUnit report uploaded with `if: always()`.
5. Push the branch and open a pull request.
   **Checkpoint 1:** both jobs appear in the PR checks. Record their durations and which one is slower.

*Recovery:* if the workflow does not appear, check that the file is under `.github/workflows/` on the branch and that the YAML parses. A workflow with a syntax error is silently absent from the checks list, which is worse than a failure.

## Part 2: make lint fail, then pass (30 minutes)

6. Introduce three deliberate problems: an unused import, a line over the limit, and an unsorted import block.
7. Push. Read the annotation: file, line, rule code.
   **Checkpoint 2:** the check is red, and the message names a rule you can look up.
8. Fix them properly (not with `# noqa`), push, and confirm green.

## Part 3: the model validation workflow (60 minutes)

9. Create `model-validation.yml` with a `pull_request` trigger filtered to `params.yaml`, `src/raviride_eta/**`, `data/raw/**`, and `requirements-serve.txt`, plus `workflow_dispatch`.
10. Add steps in this order: install dependencies, validate the raw batch, reproduce the pipeline, run the gate, upload `metrics.json` and `models/run_meta.json` with `if: always()`.
11. Set `timeout-minutes: 15` on the job.
    **Checkpoint 3:** open a PR that changes only a Markdown file; the validation workflow does not run. Change `params.yaml`; it runs.

## Part 4: block a regression (45 minutes)

12. On a branch, degrade the model: 60 trees, depth 2, 40 samples per leaf.
13. Push and watch the gate.
    **Checkpoint 4:** the job fails with exit code `1`, and the log shows both the overall and the Z08 comparison with numbers.
14. Confirm the artifact from the failed run is downloadable and contains the degraded `metrics.json`.
    **Checkpoint 5:** you can read the failing metric from the artifact without re-running anything.
15. Restore the parameters and push. The gate passes.

## Part 5: make it binding (30 minutes)

16. Configure branch protection on `main`:
    - require a pull request;
    - require the `lint`, `test`, and `validate` checks;
    - require the branch to be up to date before merging;
    - require review for changes to `baseline.json` and `params.yaml` (CODEOWNERS).
17. Try to merge the degraded branch with the failing check. Record what the UI refuses to do.
    **Checkpoint 6:** the merge button is disabled, not merely discouraged.

18. Ask a colleague (or a second account) to approve a change to `baseline.json` in the same PR as a model change. Explain in your evidence file why this is a gate loophole and which of the three defences from the module page you would adopt.

## Part 6: secrets and evidence (30 minutes)

19. Add a step that echoes a fake secret and observe the masking:
    ```yaml
    env:
      DEMO_TOKEN: ${{ secrets.DEMO_TOKEN }}
    run: echo "token is $DEMO_TOKEN"
    ```
    Create the repository secret first. Record what the log shows and what it does not.
20. Try `echo "$DEMO_TOKEN" | base64` and record whether the masked value appears. Delete the step afterwards.
    **Checkpoint 7:** you can state two ways a secret leaks despite masking.

21. Write `docs/ci-evidence.md`: the two workflow files, durations, the failing gate log, the artifact contents, the branch protection settings, and a section titled "what a green build does not prove" with at least four items.

## Expected outputs

| Output | Reference observation |
|---|---|
| Lint | 16 findings on first run, `All checks passed!` after fixes |
| Tests | 10 passed, JUnit report ~1 KB with 10 cases |
| Pipeline in CI | MAE 2.7686, gate PASS |
| Degraded model | MAE 3.4416; gate FAIL on overall and Z08; exit `1` |
| Restored model | gate PASS, exit `0` |
| PR with only a README change | validation workflow skipped |
| Merge with a failing check | blocked by branch protection |

Local verification (no GitHub remote) produced the lint, test, pipeline, and gate results above; the two workflows validated against the official schema. GitHub-specific observations must come from your own repository.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Triggers | Fast checks on every PR; model validation only on relevant paths |
| Permissions | `contents: read` explicitly set; no broader scope without a reason |
| Ordering | Model validation does not run when tests fail |
| Evidence | Failed runs still upload the report and metrics |
| Gate | Non-zero exit on regression; a required check, not a comment |
| Secrets | No secret in source, logs, artifacts, or a command line |
| Honesty | The evidence file names at least four things CI does not prove |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Workflow does not appear in the PR | YAML syntax error, or the file is not on the branch | Validate the YAML; check the path and the branch |
| `Resource not accessible by integration` | Token lacks a permission the step needs | Add the specific scope to `permissions` for that job |
| Gate passes locally, fails in CI | Different data, Python version, or baseline | Print versions and the baseline hash at the start of the gate |
| Cache restores an old metric | `metrics.json` cached | Remove it from the cache; cache dependencies only |
| Secret prints as `***` but breaks the command | Masking hides the value from you too | Test with a non-secret value first |
| Fork PR cannot access secrets | By design | Use `pull_request`, not `pull_request_target`; do not run privileged steps on fork code |
| Job runs for 40 minutes | No timeout, or the model gate on every push | `timeout-minutes`, path filters, and move the gate to PRs only |

## Cleanup

- Delete the lab branches and close the test pull requests.
- Remove the `DEMO_TOKEN` secret.
- Keep the workflows and the evidence file; they are the module's output.
- If you created a throwaway repository, delete it or make it private.

## Optional extensions

1. **Run locally with `act`.** Install `act` and run the `lint` job in Docker. Record which parts of the workflow behave differently from GitHub (secrets, artifacts, runner image). Requires Docker.
2. **Container job.** Add a job that builds the Module 11 image and runs `/health` against it. Keep it on `main` only, and explain why pulling in a fork PR is unsafe.
3. **Baseline from the registry.** Change the gate to read the baseline from the registry alias instead of `baseline.json`, and compare the trade-offs: tamper resistance versus availability and speed.

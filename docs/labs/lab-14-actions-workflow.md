# Lab 14 · Build a CI workflow that can fail

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L14 | Advanced | 3 hours | [12 · CI/CD for ML](../modules/12-ci-cd/index.md) | Partly: linted and simulated locally; hosted runners not executed |

**Starter kit:** [`examples/labs/lab-14-actions-workflow/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-14-actions-workflow) — starter files, data generator, and acceptance checker.

## Scenario

The repository has a workflow named `quality`. It is green on every push. It is
green because it does not check out the code, installs the wrong requirements,
and ends its test step with `|| true`. The badge is decorative, and a reviewer
has started treating it as evidence.

You will fix the workflow and prove it can go red. A gate nobody has seen fail is
not a gate.

## What you will be able to do

- Write a workflow that runs on pull requests with least privilege.
- Pin actions and quote the Python version so YAML cannot reinterpret it.
- Cache dependencies and measure what the cache saves.
- Simulate a workflow's commands locally, and make it fail for the right reason.

## Prerequisites and setup

```bash
cd examples/labs/lab-14-actions-workflow
python -m pip install -r requirements-dev.txt
python lint_workflow.py
python simulate_ci.py
```

Expected: `4/12 workflow checks passed`, then a simulation that "passes" while
having run almost nothing. No GitHub account or network is needed.

!!! note "What is and is not verified"
    `lint_workflow.py` and `simulate_ci.py` were executed. GitHub Actions itself
    was not: this environment has no runner and no repository remote. The
    workflow syntax, permissions and step order are checked statically, and the
    `run:` commands are executed locally. Parts 6 and 7 describe the hosted check
    you should perform once the workflow is pushed.

## Your task

Rewrite `.github/workflows/quality.yml` until the lint passes, then prove the
gate fails when a defect is injected.

## Data and starter files

| File | Purpose |
|---|---|
| `.github/workflows/quality.yml` | The broken workflow |
| `lint_workflow.py` | Twelve structural and safety checks |
| `simulate_ci.py` | Runs the workflow's `run:` steps locally, in order |
| `src/sessionlab/scores.py`, `tests/test_scores.py` | Small, real code and tests |
| `requirements-dev.txt` | ruff and pytest, pinned |

## Steps

### 1. Read the lint failures

```bash
python lint_workflow.py
```

Failures include: no `pull_request` trigger, `permissions: write-all`, no
timeout, `checkout@main`, an unquoted `python-version: 3.12`, no cache, `|| true`
on the test step, and no lint step at all.

### 2. Fix the trigger and permissions

Run on `push` to `main` and on every `pull_request`. Set `permissions: contents:
read` — the job needs to read code and nothing else.

### 3. Pin the interpreter and the actions

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: pip
```

Unquoted `3.12` is parsed by YAML as a float and can arrive as `3.12.0` or `3.1`;
quoting is not cosmetic.

### 4. Order the steps and remove the escape hatch

Install → lint → test. Delete `|| true`. A failing test must stop the job.

### 5. Run the simulation

```bash
python simulate_ci.py
```

Expected: `ruff` then `pytest`, both passing, installation reported as skipped
because the simulation never touches the network.

### 6. Prove the gate fails

```bash
python simulate_ci.py --inject-lint-error
```

This writes a module with an unused import, runs the workflow's commands, and
expects the lint step to fail. Expected:
`gate verdict: caught the injected defect`.

### 7. Run the checker

```bash
python check_lab14.py
```

Expected: `8/8 checks passed`.

### 8. Hosted verification (when you push)

Once the workflow is in a repository:

1. Open a pull request with a deliberately failing test and confirm the check is
   red and the merge button is blocked by branch protection.
2. Fix the test and confirm the same check turns green without a new commit to
   the workflow.
3. Open the run log and confirm the Python version, the cache hit line, and that
   no secret value is printed.
4. Record the run URL and the duration in your evidence file.

## Expected output

```text
  [PASS] the workflow passes every structural check -- 12/12 workflow checks passed
  [PASS] the workflow's commands pass locally -- workflow simulation: passed
  [PASS] lint runs before tests -- order in the simulated log
  [PASS] an injected defect fails the gate -- gate verdict: caught the injected defect
  [PASS] no step swallows a failure -- searched for || true and continue-on-error
```

## Acceptance criteria

| # | Criterion | How it is checked |
|---|---|---|
| 1 | Runs on pull requests | Trigger parsed |
| 2 | Least privilege | `permissions` is not `write-all` |
| 3 | Runner and timeout on every job | Job keys present |
| 4 | Checkout first | First `uses:` |
| 5 | Actions pinned | No `@main`/`@master` |
| 6 | Python version quoted | String type in YAML |
| 7 | Dependencies cached | `cache` in `with` |
| 8 | Lint before test | Command order in simulation |
| 9 | No `|| true`, no `continue-on-error` | Text scan |
| 10 | Injected defect fails the gate | Simulation exit 0 with `caught` |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Lint says `runs on pull requests -- None` | YAML parsed `on` as boolean `True` | The linter handles both; if you wrote `"on":` with quotes, remove them |
| Simulation runs `pip install` | Expected; it is skipped by design | Do not add network steps to the simulation |
| `ruff: command not found` | Dev requirements not installed in the active environment | `pip install -r requirements-dev.txt` |
| Injected defect passes | Lint step removed or non-blocking | Restore `ruff check src tests` without `|| true` |
| Cache never hits on the hosted runner | `cache-dependency-path` points at a missing file | Use `requirements-dev.txt` |

## Reflection questions

1. Which single line in the starter workflow made every other check meaningless,
   and why?
2. Why does a workflow need `pull_request` as well as `push`?
3. The simulation skips installation. What class of failure can it therefore
   never catch, and what does that imply about trusting it?
4. If `ruff` and `pytest` disagree about whether a change is acceptable, which
   one would you make blocking, and why?

## Optional extension

Add a second job that runs the tests on Python 3.11 and 3.12 with a matrix, and a
`needs:` dependency so the test job only runs after lint. Then measure the
wall-clock difference in the simulation and explain why the hosted runner may not
show the same improvement.

## Cleanup

```bash
rm -rf .pytest_cache .ruff_cache artifacts
```

PowerShell: `Remove-Item .pytest_cache, .ruff_cache, artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] The workflow lints 12/12
- [ ] The local simulation runs lint before tests
- [ ] An injected defect is caught
- [ ] Nothing swallows a failure
- [ ] `check_lab14.py` reports `ACCEPTED`
- [ ] I recorded whether hosted verification was possible

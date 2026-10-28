# Concepts · Making the checks unavoidable

## 1. Three different things called CI

The terms are used loosely; the distinctions matter for what you build.

| Practice | Trigger | Output |
|---|---|---|
| **Continuous integration (CI)** | Every push or pull request | Evidence that the change is sound: lint, tests, data checks, a model gate |
| **Continuous delivery** | A passing CI run on the main branch | A versioned, deployable artifact (image, package) that *could* ship |
| **Continuous deployment** | The same, plus an automatic release | Traffic moved without a human |

Most teams need CI and delivery; automatic deployment is a separate decision that depends on the product's tolerance for a bad release. Module 12 builds the first two. Orchestration — scheduled retraining, retries, dependencies between jobs — is Module 13 and is a different tool for a different problem.

## 2. Anatomy of a workflow

```yaml
name: ci
on: [pull_request]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pytest
```

- **Workflow** — one YAML file in `.github/workflows/`.
- **Event (`on`)** — what starts it.
- **Job** — a set of steps on one runner. Jobs run in parallel unless `needs` says otherwise.
- **Step** — a shell command (`run`) or an action (`uses`).
- **Runner** — the machine. `ubuntu-latest` is a GitHub-hosted VM image that changes over time.
- **Action** — a reusable step, referenced by repository and version.

Each `run` step starts a fresh shell, but they share the workspace and the runner's filesystem. `cd` in one step does not affect the next; environment variables set with `echo "X=1" >> $GITHUB_ENV` do.

## 3. Triggers: run what needs running

```yaml
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
```

Three practical rules:

1. **Pull requests are the important trigger.** They gate the merge, which is the only moment a change can be stopped cheaply.
2. **Path filters prevent waste**:

   ```yaml
   on:
     pull_request:
       paths:
         - "params.yaml"
         - "src/raviride_eta/**"
         - "data/raw/**"
   ```

   A documentation change should not retrain a model. The risk is a missed dependency: if the gate depends on `baseline.json` and that path is not listed, a baseline change will not trigger validation. List every input to the job, not just the obvious ones.

3. **`workflow_dispatch`** gives a manual button, which is useful while building and for re-running after an infrastructure blip.

Scheduled triggers (`schedule:`) exist but belong to orchestration thinking (Module 13): a cron job that retrains is not CI, because it is not validating a change.

## 4. Jobs, matrices, and ordering

```yaml
jobs:
  lint:
    ...
  test:
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
```

- Jobs run in **parallel** by default. A matrix fans one job into several combinations.
- `fail-fast: false` keeps the other matrix legs running when one fails, so a single run tells you whether the problem is version-specific.
- `needs: test` creates an ordering: the model gate runs only if tests passed. That is a cost decision — do not spend ten minutes training a model when a unit test already failed.
- `timeout-minutes` is not optional in practice. A hung step consumes the default limit (360 minutes on GitHub-hosted runners) and blocks the queue.

## 5. Runners are not reproducible by default

`ubuntu-latest` is a moving target: the image is updated, preinstalled tools change, and the underlying Ubuntu version moves over time. A build that passed in March can fail in June for reasons unrelated to your code.

Mitigations, in order of effort:

- pin the runner (`ubuntu-24.04`) rather than `-latest`;
- pin Python and every package (as in Module 11);
- pin actions by commit SHA for anything security-relevant;
- record the image or container digest in the build output when it matters.

The CI environment is a dependency like any other. Treating it as a constant is how "it passed yesterday" becomes an investigation.

## 6. Caching: dependencies yes, evidence no

Caching shortens runs. It also creates the possibility of testing something other than what you think.

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: pip
```

The cache key is derived from the dependency files. Change `requirements-serve.txt` and the cache is rebuilt; change nothing and the install is skipped. That is safe because the inputs determine the output.

Unsafe caching:

- **`metrics.json`, model artifacts, feature files.** If CI restores a cached metric instead of computing it, the gate validates last week's model. The cache key would have to include every input that affects the result, which is the pipeline's job, not the cache's.
- **The whole `.git` directory or the workspace.** Cheap, and it can resurrect files deleted in the branch.
- **Secrets.** Never in a cache.

Rule of thumb: cache what is expensive to *download* and cheap to *verify* (wheels, system packages). Recompute what the job exists to prove.

## 7. Artifacts and logs

A failing run is evidence; artifacts preserve it.

```yaml
- name: Upload test report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: junit-${{ matrix.python-version }}
    path: reports/junit.xml
```

- `if: always()` matters: without it, the upload is skipped when the test step fails, which is exactly when you need the report.
- Artifacts expire (default 90 days, configurable). Long-lived evidence belongs in a system designed for it — the registry, an object store, or a metrics database.
- Logs are not artifacts. They are truncated, hard to query, and disappear with retention. If a number matters, write it to a file and upload it.

The reference run produces a JUnit report of about 1 KB with ten test cases, and a `metrics.json` with the overall and per-zone results. Both are small, both are the actual evidence.

## 8. Secrets, permissions, and the two ways to leak

**Permissions.** The workflow's `GITHUB_TOKEN` is a credential. Set it explicitly:

```yaml
permissions:
  contents: read
```

Without a `permissions` block, the token's scopes depend on repository settings and may include write access to contents, packages, or issues. A compromised dependency in a test step then has the same access. Grant the minimum, per job if necessary.

**Secrets.** `${{ secrets.NAME }}` is injected into the step's environment or arguments. It is masked in logs when printed exactly, but masking is a string match, not a guarantee:

- a secret embedded in JSON, base64, or a URL may not be masked;
- `set -x`, verbose HTTP clients, and stack traces can print request headers;
- a secret written to a file can be uploaded as an artifact;
- a secret passed to a third-party action is visible to that action.

Two leaks are common enough to name:

1. **`echo $SECRET` in a debugging commit.** Masking catches the exact value; it does not catch `echo $SECRET | base64`.
2. **`pull_request_target` with a checkout of the PR head.** This event runs in the base repository's context *with secrets*, and checking out untrusted code then executing it hands those secrets to the contributor. Use `pull_request` for anything that runs PR code. If you need `pull_request_target` to comment on a PR, never check out or execute the head.

For cloud access, prefer **OIDC** over long-lived keys: the workflow exchanges a short-lived token for cloud credentials, so there is no static secret to leak or rotate.

## 9. Supply chain: the actions you did not write

Every `uses:` is code you run with your token and your secrets.

- Pin to a full commit SHA for third-party actions: `uses: owner/action@<40-char-sha>`. Tags are mutable; a compromised maintainer can move one.
- Prefer official actions (`actions/*`) for checkout, setup, and artifacts.
- Be cautious with actions that need broad permissions or secrets.
- Review what an action does before adding it; "it is popular" is not a security review.

This is not paranoia for its own sake. A CI pipeline typically holds the credentials to deploy, which makes it a high-value target.

## 10. Branch protection: where a check becomes a rule

A workflow that fails is informative. A **required status check** is binding: the branch cannot merge until it passes. That is the difference between a suggestion and a control.

Typical configuration for `main`:

- require a pull request before merging;
- require the `lint` and `test` checks, and the `validate` job;
- require the branch to be up to date before merging (prevents "passed on an old base");
- require review from a code owner for protected paths (`baseline.json`, `promotion_policy.yaml`);
- disallow bypass for administrators, or make bypass auditable.

What it still does not prevent: a maintainer with admin rights can change the rules; a required check can be satisfied by a workflow that no longer tests what it claims; and a green run on a stale branch can be merged if "up to date" is not required.

## 11. A model gate in CI

The gate answers one question: *is this candidate worse than the baseline by more than we tolerate?* In CI it has three inputs:

| Input | Where it comes from | Risk |
|---|---|---|
| Candidate metrics | Computed in this run | Stale cache, different data |
| Baseline | Repository file or registry | Editable by the same PR |
| Tolerance | Repository policy | Loosened to make the build pass |

The reference gate prints both comparisons:

```text
FAIL overall mae 3.4416 (baseline 2.7686, allowed 2.9070, tolerance 5%)
FAIL Z08 mae 7.3065 (baseline 5.5812, allowed 6.4184, tolerance 15%)
```

Two design decisions are worth stating explicitly in the workflow:

- **What counts as the baseline.** A file in Git is simple and reviewable; a registry alias is authoritative and harder to tamper with. Both are defensible; silence is not.
- **What happens on failure.** A comment is advisory; a non-zero exit with a required check is binding. The reference gate exits `1`, and the workflow inherits that.

A gate that only warns is a gate that will be ignored during a deadline. That is not cynicism; it is the observed behaviour of every advisory check in every organisation.

## 12. Building the image in CI

The container from Module 11 should be built by the same workflow that tests the code, so the image is never assembled by hand:

```yaml
- name: Build image
  run: docker build -t raviride-eta:${{ github.sha }} .
```

Two rules:

- **Build once, promote the digest.** Rebuilding for each environment produces subtly different images.
- **Do not push without a registry and credentials.** Pushing to a public registry from a fork PR is a supply-chain incident waiting to happen; gate publishing on the main branch and a protected environment.

The authoring machine had no Docker daemon, so this step is described and not executed here; the lab marks it accordingly.

## 13. Cost and speed

CI minutes are money and attention. The effective levers:

- **Path filters** — do not run the model gate for a README change.
- **`concurrency` with `cancel-in-progress`** — push three commits, keep the last run.
- **Ordering** — lint before tests before the pipeline, so cheap failures stop expensive work.
- **Caching** — dependencies, as above.
- **Sharding** — split a slow test suite, only once it is genuinely slow.

A ten-minute pipeline that runs on every push trains people to push less often and batch changes, which is the opposite of continuous integration. If the model gate is slow, run it on pull requests to `main` and on a nightly schedule, not on every commit to a feature branch.

## 14. What a green build does not prove

- It does not prove the model is good, only that it is not worse than the baseline by more than the tolerance.
- It does not prove the data is representative; validation checks structure, not meaning.
- It does not prove the service works in production; the contract tests use a test client, not a real deployment.
- It does not prove the environment matches production, unless the image is the same digest.
- It does not prove the gate was honest; a loosened tolerance passes everything.

Write these down in the repository. A team that believes CI proves more than it does will skip the checks that matter when an incident happens.

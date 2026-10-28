# Worked example · Two workflows, one refusal, and what was not run

The repository gets two workflow files. Both were validated and every command inside them was executed locally. Neither was executed by GitHub Actions, because this project has no GitHub remote — that boundary is stated again at the end, with the checks that remain unverified.

## The fast workflow

`.github/workflows/ci.yml` — lint and tests on every push and pull request:

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: python -m pip install "ruff==0.7.4"
      - run: ruff check src serving tests scripts

  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: python -m pip install -r requirements-serve.txt -r requirements-dev.txt
      - run: python -m pytest --junitxml=reports/junit.xml
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: junit-${{ matrix.python-version }}
          path: reports/junit.xml
```

Three choices worth defending:

- `permissions: contents: read` — the jobs only need to read the repository. Without this block, the token's scope depends on repository settings.
- `cancel-in-progress: true` — a branch pushed three times should run the third version, not queue three.
- `fail-fast: false` — a failure on 3.11 should not cancel 3.12, because the comparison is the information.

## The slow workflow

`.github/workflows/model-validation.yml` — data check, pipeline, regression gate, only when something that affects the model changes:

```yaml
on:
  pull_request:
    paths:
      - "params.yaml"
      - "src/raviride_eta/**"
      - "data/raw/**"
      - "requirements-serve.txt"
  workflow_dispatch:

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12", cache: pip}
      - run: python -m pip install -r requirements-serve.txt
      - name: Validate the raw batch
        run: python -m raviride_eta.data data/raw/trips.csv
        env: {PYTHONPATH: src}
      - name: Reproduce the pipeline
        run: |
          python -m raviride_eta.prepare
          python -m raviride_eta.featurise
          python -m raviride_eta.train
          python -m raviride_eta.evaluate
        env: {PYTHONPATH: src}
      - name: Regression gate
        run: python scripts/check_metrics.py --baseline baseline.json --current metrics.json --tolerance 0.05
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: metrics
          path: |
            metrics.json
            models/run_meta.json
```

The path filter is the load-bearing part: a model gate that runs on a typo fix will be disabled by the first person who has to wait for it.

## Validation that could be done without GitHub

**The YAML matches the official schema.** Using `check-jsonschema` with SchemaStore's GitHub workflow schema:

```text
$ check-jsonschema --schemafile https://json.schemastore.org/github-workflow.json \
    .github/workflows/ci.yml .github/workflows/model-validation.yml
ok -- validation done
```

That catches misspelled keys (`runs-onn`), wrong types, and invalid enum values. It does not catch a command that fails.

**The commands, executed locally.** In order, exactly as the workflow runs them:

```text
$ python -m raviride_eta.data data/raw/trips.csv
PASS data/raw/trips.csv: 1200 rows, 8 checks
$ python -m raviride_eta.prepare
test:  304 rows 2026-09-22 02:04:00 .. 2026-09-28 23:23:00
cutoff: 2026-09-22 00:00:00
$ python -m raviride_eta.featurise
test: 304 rows, added ['hour', 'day_of_week', 'is_weekend', 'is_peak', 'log_distance'] -> test.csv
$ python -m raviride_eta.train
trained full model on 896 rows -> model.joblib
$ python -m raviride_eta.evaluate
MAE 2.7686 min | RMSE 4.4922 | R2 0.7319 | p95 8.254 min
$ python scripts/check_metrics.py --baseline baseline.json --current metrics.json --tolerance 0.05
PASS overall mae 2.7686 (baseline 2.7686, allowed 2.9070, tolerance 5%)
PASS Z08 mae 5.5812 (baseline 5.5812, allowed 6.4184, tolerance 15%)
model is within tolerance
```

**The test evidence.** `pytest --junitxml=reports/junit.xml` produced a 1,100-byte report with ten test cases, all passing:

```text
$ python -m pytest --junitxml=reports/junit.xml
10 passed, 17 warnings in 2.53s
$ head -3 reports/junit.xml
<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest"
errors="0" failures="0" skipped="0" tests="10" time="2.529" ...>
```

That is the artifact the workflow uploads. It is small, it is the actual evidence, and it exists even when the step fails — provided the upload uses `if: always()`.

## The lint failure that had to be fixed first

The first `ruff check` on this codebase found 16 problems. Four representative ones:

```text
scripts/check_metrics.py:10:8: F401 `sys` imported but unused
src/raviride_eta/prepare.py:7:18: F401 `pandas` imported but unused
tests/test_api.py:8:8: F401 `joblib` imported but unused
src/raviride_eta/data.py:3:1: I001 Import block is un-sorted or un-formatted
```

Nine were fixed mechanically (`ruff check --fix`), and the rest by hand: long f-strings split, an import block reordered, a `zip()` given `strict=True`. The final run:

```text
$ ruff check src serving tests scripts
All checks passed!
```

Two notes for the record. The unused `joblib` import in the tests was left over from the version of the contract test that loaded the wrong artifact — a real symptom, not lint noise. And two scripts legitimately bootstrap `sys.path`, so `E402` and `I001` are ignored for those files in `pyproject.toml`, with a comment saying why. A suppression with a reason is a decision; a bare `# noqa` is a habit.

## The gate that blocked a model

To prove the gate is not decorative, the model was degraded deliberately: 60 trees, depth 2, 40 samples per leaf.

```text
$ python -m raviride_eta.train && python -m raviride_eta.evaluate
test rows: 304
MAE 3.4416 min | RMSE 5.2113 | R2 0.6392 | p95 9.4972 min

$ python scripts/check_metrics.py --baseline baseline.json --current metrics.json --tolerance 0.05
FAIL overall mae 3.4416 (baseline 2.7686, allowed 2.9070, tolerance 5%)
FAIL Z08 mae 7.3065 (baseline 5.5812, allowed 6.4184, tolerance 15%)
model regression:
  - overall mae 3.4416 exceeds 2.9070
  - Z08 mae 7.3065 exceeds 6.4184
```

Exit code `1`, which is what the workflow step returns, which is what the required check reports. Restoring the parameters and rerunning returned both lines to `PASS` and exit `0`.

The Z08 line is the interesting one. A 24% degradation in one zone would have been invisible in the overall number if the overall had stayed within 5%; the gate checks both because Module 06 established that the aggregate hides the population.

## Secrets: the shape of a correct step

The reference workflows need no secrets. If a later step pushes an image or comments on a pull request, the shape is:

```yaml
- name: Push image
  env:
    REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
  run: |
    echo "$REGISTRY_TOKEN" | docker login ghcr.io -u "${{ github.actor }}" --password-stdin
```

and the shapes to avoid:

```yaml
# Leaks into the log as a command argument, and into shell history
run: docker login -p ${{ secrets.REGISTRY_TOKEN }}

# Prints the value; masking catches the exact string but not transformations
run: echo "token is $REGISTRY_TOKEN"

# Writes a credential into an uploaded artifact
run: python dump_config.py > config.txt
```

The rule is not "never use secrets"; it is "pass them through stdin or a file the step reads, never through a command line, a log line, or an artifact".

## What was not executed

| Check | Status |
|---|---|
| Workflow YAML validates against the GitHub schema | Verified (`ok -- validation done`) |
| Lint command works and fails on real findings | Verified locally (16 → 0) |
| Tests run and produce a JUnit artifact | Verified locally (10 passed, 1,100-byte XML) |
| Pipeline reproduces the metric | Verified locally (MAE 2.7686) |
| Gate fails a degraded model with exit `1` | Verified locally |
| GitHub actually runs the workflows | **Not verified** — no remote |
| Matrix on 3.11 and 3.12 in Actions | **Not verified** — 3.12 only here |
| `permissions`, caching, concurrency behaviour | **Not verified** — runner features |
| Branch protection blocking a merge | **Not verified** — repository setting |
| Docker build step | **Not verified** — no daemon (Module 11) |

The unverified rows are the ones that need a repository, not more code. The lab walks through them; treat any claim about GitHub's behaviour that you have not observed as a hypothesis.

## What this establishes

A CI pipeline is a sequence of commands with an audience. The commands are the same ones you ran by hand; the difference is that the audience — the merge button — cannot be persuaded to ignore them. Everything else, including the flattering green check, is presentation.

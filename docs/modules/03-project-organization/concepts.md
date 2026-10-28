# Concepts · Module 03

## 1. Four things that change for different reasons

A project has four kinds of content, and they are edited by different people at different times:

| Content | Changes when | Lives in | Must never contain |
|---|---|---|---|
| Code | Behaviour must change | `src/` | Paths, thresholds, credentials |
| Configuration | Environment or experiment changes | `params.yaml`, env vars | Logic |
| Data | The world changes | Versioned data store | Code |
| Outputs | A run completes | `models/`, `metrics.json` | Anything hand-edited |

The rule is not aesthetic. Each kind has a different change rate, review process, and storage mechanism. Code is reviewed line by line and stored in Git. Data is large and stored by content hash (Module 04). Outputs are disposable and regenerated. Configuration sits between code and environment: reviewed like code, changed more often.

When these mix, every change becomes expensive. A threshold buried in a training script requires a code review and a redeploy; the same threshold in `params.yaml` requires a one-line diff.

## 2. Notebooks are for thinking; modules are for running

A notebook is excellent for exploration: it keeps outputs beside code, it allows out-of-order execution, and it makes a result easy to show. Those same properties make it a poor production artefact: hidden state, unreproducible order, and no way to import one cell.

The migration does not require abandoning notebooks. It requires the *logic* to live in modules, with notebooks importing them:

```python
from raviride_eta.features import add_features
from raviride_eta.train import train_model

frame = add_features(df)
model = train_model(frame, params)
```

Then a notebook explores, and the pipeline runs the same functions. The test for whether the extraction worked: delete the notebook. If the pipeline still trains, the logic was in the right place.

## 3. The configuration layer

Configuration is any value that differs between environments or experiments. Paths, hyperparameters, date windows, thresholds, feature sets.

Three storage choices, in order of preference:

1. **A file in the repository** (`params.yaml`): reviewable, diffable, versioned with the code that reads it. Use for anything that changes per experiment.
2. **An environment variable**: for values that differ per machine or deployment and must not be committed - database URLs, API endpoints.
3. **A secret manager**: for credentials. Never in the repository, never in a notebook output, never in a log line.

The distinction that matters most: **a setting is configuration; a credential is a secret.** Settings can be reviewed by anyone; secrets must be readable by as few people as possible. Putting an API key in `params.yaml` "because it is configuration" is how keys end up in Git history.

Configuration code should be boring and central:

```python
def load_params(path: str | Path | None = None) -> dict:
    with (Path(path) if path else PROJECT_ROOT / "params.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)
```

One loader, one schema. Every module calls it; nothing else parses YAML. When you later add a parameter, you change one file and every stage sees it.

## 4. Architecture decision records

An ADR is a short, numbered document recording a decision that was not obvious. Not a design document, not a tutorial: a record of *why*, written when the decision is made, so the next person can either follow it or overturn it deliberately.

Format (Michael Nygard's, still the most useful):

```markdown
# ADR 0002: Configuration in params.yaml, secrets in environment variables

## Status
Accepted - 2026-10-14

## Context
Stages need shared parameters (test window, seed, model depth). The legacy
script hard-coded them in three places. A database password is also needed
by the (future) tracking server.

## Decision
Non-secret parameters live in params.yaml, loaded through config.load_params().
Secrets are read from environment variables and never written to disk.

## Alternatives considered
- Environment variables for everything: rejected, values become invisible in review.
- A Python settings module: rejected, changing a value would be a code change.

## Consequences
- A parameter change is a one-line diff, visible in review.
- params.yaml must be passed to DVC as a tracked parameter (Module 05).
- Secrets require documentation of required variables, not values.
```

Two rules make ADRs useful. Number them sequentially, and never edit an accepted ADR - supersede it with a new one. A decision log you rewrite is a decision log nobody trusts.

## 5. Technical debt, priced

Module 01 named the categories. Here is how to make them manageable: a **debt register** is a table where each item has a symptom, a risk, a fix, and a cost.

| Field | Example |
|---|---|
| ID | D-03 |
| Category | Configuration debt |
| Symptom | Test date window hard-coded in `prepare.py` and in the notebook |
| Risk | A changed window silently produces incomparable metrics |
| Fix | Move to `params.yaml`, pass through `config.load_params()` |
| Cost | S (1 hour) |
| Owner role | Whoever owns the training pipeline |

Two habits separate a register from a wish list:

- **Price everything**, even roughly. "S/M/L" is enough. Unpriced debt never gets scheduled.
- **Record the decision to keep it.** Some debt is correct for now. Write "accepted until Module 05" rather than pretending it will be fixed "soon".

## 6. Linting: removing style from review

Most review comments are about things a machine can check: unused imports, line length, mutable defaults, shadowed names. `ruff` checks them in milliseconds.

```powershell
ruff check .
```

Configuration belongs in `pyproject.toml` so every machine runs the same rules:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

Start with the defaults and add rules deliberately. A lint rule nobody understands is noise; the aim is to delete arguments, not to win them.

`pre-commit` runs the same checks before a commit exists. It is optional in this course because it needs its own install step, but the effect is worth knowing: the check moves from "the reviewer notices" to "the commit cannot be made".

## 7. Dependency direction

A structure is only as good as its import graph. The rule for this project:

```text
config  <-  data  <-  features  <-  train  <-  evaluate
```

Arrows point one way. `config` knows nothing about the others; `features` imports nothing that reads files; `evaluate` imports the model loader but not the trainer. When you find a cycle, the cause is usually a shared helper that belongs lower in the graph - or two responsibilities that should be one module.

Why it matters in practice: a cycle means you cannot test one module without importing the whole project, and you cannot change one without risking all of them.

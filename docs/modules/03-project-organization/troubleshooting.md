# Troubleshooting · Module 03

## The refactor changed the metric

This is the most important problem in the module, so diagnose it in this order.

| Check | What to compare | If they differ |
|---|---|---|
| Row counts | `len(train)`, `len(test)` before and after | Split boundary: `<` versus `<=`, or `normalize()` missing on the cutoff |
| Row order | `train["requested_at"].is_monotonic_increasing` | Sorting moved after the split; sort before splitting |
| Seed | `random_state` in `params.yaml` versus the legacy literal | Fix the value, not the model |
| Feature list | `x_train.columns.tolist()` | A column was added or dropped during extraction |
| Categorical handling | Presence of `OneHotEncoder(handle_unknown="ignore")` | Sklearn's default changed, or the category order changed |
| Missing values | `df.isna().sum()` | A fill (or its absence) was moved to a different stage |

A useful debugging technique: write both versions' `train` frames to CSV, `compare` them, and diff. Most "the model changed" problems are "the data changed" problems.

## Import problems

**Circular import.** Symptom: `ImportError: cannot import name 'X' from partially initialized module`.

Cause: module A imports B, B imports A. In this project the usual culprits are `config` importing a stage, or `features` importing `train` for the feature list.

Fix by assignment: decide which module owns the shared thing. If both need a column list, it belongs in `features`; if both need a path, it belongs in `config`. Never fix a cycle with a local import inside a function unless you can explain why the dependency is genuinely deferred.

**`ImportError` only inside tests.** The test imports a module that runs code at import time. Stages should do work inside `main()`, not at module level - this is why every stage module here ends with `if __name__ == "__main__": main()`.

## Configuration problems

| Symptom | Cause | Fix |
|---|---|---|
| `KeyError: 'model'` | YAML nesting | `params["model"]["max_depth"]`, and the YAML must have a `model:` mapping |
| Parameter change has no effect | The code still has a literal | Search for the number: `rg "200" src/` |
| Stage runs from the wrong directory | Paths built from the current directory | Anchor paths to `Path(__file__).resolve().parents[2]` |
| YAML parses but values are strings | `"42"` quoted in YAML | Remove quotes for numbers; `safe_load` infers types |
| Secret appears in a diff | Stored in `params.yaml` | Rotate it, move to an environment variable, add a pre-commit check |

## Linting and formatting

| Message | Meaning | Action |
|---|---|---|
| `F401 imported but unused` | Leftover import | Delete it |
| `E501 line too long` | Line exceeds `line-length` | Wrap; do not raise the limit to hide one line |
| `B006 mutable default argument` | `def f(x=[])` | Use `None` and create inside |
| `UP` rules suggest modern syntax | Project targets py311 | Accept the fix; the rule exists for the version you declared |
| `ruff` disagrees with your editor | Editor formats differently | Run `ruff format` and `ruff check --fix`, then commit both |

## When the repository itself is the problem

If you cannot explain, in one sentence each, where the following lives, the refactor is incomplete:

- the list of features the model uses;
- the number of days in the test window;
- the path to the trained artefact;
- the definition of "peak hour".

Each answer should name one file. Two files means the definition can drift.

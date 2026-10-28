# Learning objectives · Module 03

| # | Objective | Evidence |
|---|---|---|
| 1 | Separate data, code, configuration, and outputs | A repository tree where each concern has one home, and no path appears twice |
| 2 | Move logic from a script into importable modules without changing behaviour | Before/after metrics that are equal, and a `git diff` a reviewer can follow |
| 3 | Distinguish configuration from code, and secrets from settings | `params.yaml` for values, environment variables for secrets, and an explanation of the difference |
| 4 | Identify and rank technical debt | A debt register with category, symptom, risk, fix, cost, and an owner role |
| 5 | Write an actionable ADR | Two ADRs with context, decision, alternatives rejected, and consequences |
| 6 | Keep style out of review | `ruff check .` passing, with the rules recorded in `pyproject.toml` |

## The refactor review criteria

A reviewer should be able to check each of these without reading every line:

- [ ] No module imports another module that imports it back (no cycles).
- [ ] `config` holds paths and constants; it imports nothing from the other modules.
- [ ] `data` loads and validates; it does not train or print metrics.
- [ ] `features` is pure: same input row, same output row, no file access.
- [ ] `train` fits and writes an artefact; it does not compute the final report.
- [ ] `evaluate` reads an artefact and a dataset; it writes metrics.
- [ ] Every magic number that a human might change lives in `params.yaml`.
- [ ] No absolute path anywhere in tracked files.
- [ ] The original metric is reproduced exactly, and the command that reproduces it is recorded.

## Self-check before you start

You should be able to read a few hundred lines of Python and say what each function does. If not, do that first with the legacy script in the [worked example](worked-example.md); the module is about structure, not syntax.

After the module, you are done when you can answer:

1. What is the difference between configuration and a secret, and why does it change where the value lives?
2. Why is a hard-coded path debt even if it is correct today?
3. What makes a refactor safe to merge?
4. Which debt category is invisible in a code review, and why?
5. What does an ADR record that a commit message cannot?

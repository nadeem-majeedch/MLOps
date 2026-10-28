# 03 · Organizing an ML project and understanding technical debt

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Foundation | 10 hours | [Module 02](../02-python-git-cli-environments/index.md) | Essential |

The RaviRide ETA model currently lives in one 300-line script with an absolute path at the top, hyperparameters scattered through the middle, and a `if __name__ == "__main__"` block that also writes the final metrics file. It works. That is the problem: it will keep working right up until someone needs to change one thing.

This module turns that script into a package you can test, configure, and explain - without changing what it predicts.

## What you will be able to do

- Separate data, code, configuration, and outputs so each can change independently.
- Move logic out of a script into importable modules while proving behaviour is unchanged.
- Move settings into a configuration layer and say why hard-coded paths become debt.
- Recognise the six technical-debt categories in a real repository and rank them by cost.
- Write an architecture decision record (ADR) a reviewer can act on.

## Start here

1. Read [Concepts](concepts.md) sections 1–3. The rest assumes them.
2. Run the [worked example](worked-example.md) yourself with the legacy script it provides.
3. Do the [lab](lab.md): refactor, then prove the metric did not move.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives, evidence, and the refactor review criteria |
| [Concepts](concepts.md) | Separation, configuration, ADRs, debt taxonomy, linting |
| [Worked example](worked-example.md) | A single-file script split into five modules, with equivalence proved |
| [Guided lab](lab.md) | Refactor the legacy script, write two ADRs, build a debt register |
| [Independent challenge](independent-challenge.md) | Turn a "before" snapshot into a budgetable debt register |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Circular imports, drifted configs, refactors that change results |
| [References](references.md) | ADR practice, linting, and packaging sources |

## What you produce

- A package with `config`, `data`, `features`, `train`, and `evaluate` modules.
- `params.yaml` holding every value that used to be a literal.
- Two ADRs: one for the layout, one for the configuration layer.
- A debt register with at least five items, each with severity and estimated cost.
- Proof that the refactor preserved the original metric.

## Next

[Module 04 · Data quality and versioning](../04-data-quality-versioning/index.md) adds validation to the `data` module you just created and starts versioning the dataset itself.

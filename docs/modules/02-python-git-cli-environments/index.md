# 02 · Python, Git, CLI, and reproducible environments

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Foundation | 14 hours | [Module 01](../01-introduction-to-mlops/index.md) | Essential |

This is the module that makes everything else verifiable. Until a second person can rebuild your environment from your repository and get the same result, no later claim in this course - "the model is reproducible", "the pipeline passes", "the deployment works" - can be checked.

You will create the `raviride-eta` repository that the next fifteen modules build on. It starts nearly empty on purpose: every significant file added later will be one you understand.

## What you will be able to do

- Create and activate an isolated environment, and diagnose the three common reasons activation fails.
- Declare dependencies in `pyproject.toml`, pin them, and explain loose versus locked dependency sets.
- Prove reproducibility by rebuilding from the repository alone.
- Use branches and commits as a habit, and read a diff before committing.
- Read a traceback to its first useful line instead of its last.

## Start here

1. Read [Concepts](concepts.md) sections 1–4. These explain *why* a virtual environment exists, not just how to make one.
2. Do [Part 1 of the lab](lab.md#part-1-create-the-skeleton) now; you need the repository for every later module.
3. Finish the lab, then take the [knowledge check](knowledge-check.md).

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives, evidence, and a ten-item reproducibility checklist |
| [Concepts](concepts.md) | Interpreter, PATH, isolation, dependencies, layout, Git, tracebacks |
| [Worked example](worked-example.md) | Building the skeleton command by command, with real output |
| [Guided lab](lab.md) | Create the repository, then diagnose a colleague's broken environment |
| [Independent challenge](independent-challenge.md) | Rebuild from scratch and break the lock file deliberately |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Activation, import, and pip failures with fixes |
| [References](references.md) | Official documentation for every tool used |

## What you produce

- `raviride-eta/` with `pyproject.toml`, `src/` layout, `tests/`, `.gitignore`.
- A captured environment listing and a repository tree.
- A first branch and a reviewed commit.
- A short log of every error you hit and how you fixed it.

Keep the error log. It becomes evidence for the [Module 03](../03-project-organization/index.md) debt register, and it is the most useful thing you will write this week.

## Next

[Module 03 · Organizing an ML project](../03-project-organization/index.md) refactors training code out of a single script into this structure.

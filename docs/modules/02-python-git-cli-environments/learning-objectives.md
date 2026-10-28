# Learning objectives · Module 02

| # | Objective | Evidence |
|---|---|---|
| 1 | Create, activate, and rebuild an isolated environment | A terminal session where `python -c "import sys; print(sys.prefix)"` prints the project's `.venv` path |
| 2 | Explain what an environment isolates, and what it does not | Two lists: what changes inside a venv, what stays shared with the operating system |
| 3 | Declare and pin dependencies | `pyproject.toml` with version bounds, plus a lock file you generated |
| 4 | Prove a repository is reproducible | Delete `.venv`, rebuild using only the repository, run the code, show identical output |
| 5 | Use branches, diffs, and commit messages deliberately | A branch, two commits, and a `git diff` you read before committing |
| 6 | Read a traceback efficiently | Three tracebacks explained in your error log: cause, fix, and the line that revealed it |
| 7 | Navigate and compose commands | A command sequence using a pipe or redirect that produces information you needed |

## The reproducibility checklist

Ten binary criteria. Each is inspectable by someone else, which is the point. Use it on your own repository before Module 03.

- [ ] A clean clone installs with one documented command.
- [ ] The command is written in the repository, not remembered.
- [ ] Python version is declared (`requires-python`).
- [ ] Direct dependencies have version bounds.
- [ ] A lock file or fully pinned requirements file is committed.
- [ ] Generated artefacts (data, models, virtual environments) are ignored by Git.
- [ ] `python -m pytest` runs from the repository root without extra configuration.
- [ ] Imports work from a fresh shell, not only from inside an IDE.
- [ ] The README states how to run the tests and how to regenerate data.
- [ ] No absolute path appears anywhere in the tracked files.

An honest score below 10 is normal at this stage. Fix the gaps now; Module 05's pipeline and Module 12's CI both depend on them.

## Self-check before you start

You should already be able to run a Python script from a terminal and make a commit. If `git status` is unfamiliar, spend an hour on the Git book's first two chapters first.

After the module, you are done when you can answer these without notes:

1. Why does `pip install` inside a venv not affect other projects?
2. What exactly does activation change, and why can an IDE still use the wrong interpreter?
3. What is the difference between a dependency bound (`pandas>=2.2,<3`) and a lock?
4. Which files must never be committed, and what happens if one is?
5. What does the last line of a traceback tell you, and what does it not tell you?

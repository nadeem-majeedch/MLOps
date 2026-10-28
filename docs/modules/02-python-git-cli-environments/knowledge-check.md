# Knowledge check · Module 02

## Questions

1. What does activating a virtual environment change, and what does it leave alone?
2. `python -c "import raviride_eta"` fails with `ModuleNotFoundError` although `pip install -e .` reported success. Name three plausible causes.
3. Explain the difference between `pandas>=2.2,<3.0` in `pyproject.toml` and an exact pin in a lock file. Why keep both?
4. Why does this course use a `src/` layout rather than putting the package at the repository root?
5. `pip install -r colleague/requirements.txt` fails with "No matching distribution found for pandas==1.5.0". What is the actual problem, and what are the two correct fixes?
6. What does `git diff --staged` show that `git status` does not, and why does that difference matter before a commit?
7. A secret was committed and then deleted in a later commit. Is it gone? Justify your answer.
8. Reading a traceback: why is the last line not enough, and which frame should you look at first?
9. Give one command whose exit code tells you whether a test suite passed, and explain why parsing the console output instead is a bad idea.
10. Your tests pass locally but fail in CI with `ModuleNotFoundError`. What is the most likely repository defect?

## Answers and reasoning

**1.** Activation prepends the environment's scripts directory to `PATH` and sets `VIRTUAL_ENV`. It does not change the Python version, the standard library, system libraries, your data, or the interpreter your IDE uses. *Reasoning:* this is why an activated terminal and a notebook can disagree, and why "it works in my terminal" is not evidence about the notebook.

**2.** Any three of: you installed with a different interpreter than the one now running (check `sys.prefix`); the package directory is not where `[tool.setuptools.packages.find]` says it is; the `src` layout has no `__init__.py`; you ran the command from inside `src/`, so the import resolved locally and would fail elsewhere; a stale install points at a deleted path. *Reasoning:* all five produce the same message. The discriminator is `print(raviride_eta.__file__)`.

**3.** The bound states which versions you are willing to accept and lets pip resolve the rest; the lock states the exact set that was resolved and verified. Keep both because they answer different questions: the bound lets you upgrade deliberately, the lock lets you rebuild exactly. A lock without bounds silently freezes old transitives; bounds without a lock allow an unrelated release to change your build.

**4.** So that imports cannot succeed by accident from the current directory. With a flat layout, `import raviride_eta` works because the repository root is on the path, even if the package is not installed; the failure appears only in CI or on another machine. The `src/` layout forces the install to be real.

**5.** The interpreter is newer than the package builds available for it: pandas 1.5.0 has no wheel for Python 3.12. Correct fixes: recreate the environment with a Python version that supports the pin (3.11), or bump the pins to versions with 3.12 support and re-verify. Wrong fixes: `--no-deps`, forcing an old interpreter into the environment, or vendoring a wheel from elsewhere. *Reasoning:* the error names the package but describes the environment.

**6.** `git status` lists changed paths; `git diff --staged` shows the actual lines that will be committed. It matters because debugging prints, hard-coded paths, and credentials are invisible in a file list and obvious in a diff.

**7.** No. The blob remains reachable from the earlier commit and in reflogs until garbage collection; anyone with a clone already has it. The secret must be rotated. Removing it from history is a separate, disruptive operation that does not undo the exposure.

**8.** The last line names the symptom (exception type and message); the frames above locate the cause. Look first at the deepest frame that belongs to *your* code, because library frames describe mechanics you rarely control. Then ask which assumption is wrong: path, working directory, or existence.

**9.** `python -m pytest` returns 0 when all selected tests pass and non-zero otherwise. Parsing output is fragile because plugins, verbosity settings, and localisation change the text, while the exit code is a stable contract. This is the same mechanism CI relies on.

**10.** The package is not installed in CI. Either the CI step installs only `requirements.txt` (which lists packages, not your project), or the test command runs without `pip install -e .`. The local suite passed because the working directory made the import possible. *Reasoning:* the fix is to install the project itself, which is why the `src/` layout and a CI install step belong together.

## Scoring

| Score | Next step |
|---|---|
| 8–10 | Continue to Module 03 |
| 5–7 | Redo Part 4 of the lab and reread sections 4 and 8 of [Concepts](concepts.md) |
| 0–4 | Repeat the lab from Part 2 with the environment deleted first; the gap is practical, not conceptual |

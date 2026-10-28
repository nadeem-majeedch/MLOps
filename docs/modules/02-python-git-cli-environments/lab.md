# Guided lab · Build the environment, then repair a broken one

**Time:** 4 hours. **Tools:** Python 3.11 or 3.12, Git 2.40+, PowerShell 7 (or bash on Linux/macOS), a text editor. No accounts, no cloud services, no data downloads.

## Scenario and business problem

RaviRide's ETA model currently trains on one analyst's laptop. When she is on leave, nobody can reproduce her results: the notebook imports a library version nobody has, the data path points at her home directory, and the "final" model was produced by a script whose last edit is unrecorded.

Your task is to create the repository that will replace this arrangement, and then to diagnose a colleague's environment that installs successfully on his machine and fails on yours. The output is not just a working environment; it is a repository where a stranger can rebuild that environment from the files alone.

### Skills practised

- Creating and activating an isolated environment; verifying which interpreter is active.
- Declaring dependencies with bounds; installing a project in editable mode.
- Writing ignore rules that keep generated artefacts out of history.
- Using a branch, a diff, and a commit message deliberately.
- Diagnosing a dependency resolution failure from its message.

### Prerequisites

[Module 01](../01-introduction-to-mlops/index.md). Basic Python and Git. You should be able to run a script and make a commit, even if slowly.

### Input data

None. The repository is created by you. The "colleague's environment" is a five-line requirements file given in Part 4.

### Directory layout you will build

```text
raviride-eta/
├── .gitignore
├── pyproject.toml
├── README.md
├── src/
│   └── raviride_eta/
│       └── __init__.py
├── tests/
│   └── test_smoke.py
└── docs/
    └── environment-log.md
```

## Part 1: create the skeleton

1. Create the directory, initialise Git, and confirm the branch is `main`:
   ```powershell
   mkdir raviride-eta; cd raviride-eta; git init -b main
   git status
   ```
   **Checkpoint 1:** `git status` reports the current branch and no commits.
2. Create the folder structure and an empty `src/raviride_eta/__init__.py` containing `__version__ = "0.1.0"`.
3. Write `pyproject.toml` from the [worked example](worked-example.md#step-2-create-the-repository-and-the-project-file).
   *Recovery:* if pip later says "no packages found", your `[tool.setuptools.packages.find] where = ["src"]` line is missing or the package folder has no `__init__.py`.
4. Create `.gitignore` before installing anything. Copy the block from the worked example.
   **Checkpoint 2:** `git status --short` lists only `pyproject.toml`, `.gitignore`, and `src/`.

## Part 2: environment and install

5. Create and activate the environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
6. Verify the interpreter:
   ```powershell
   python -c "import sys; print(sys.prefix)"
   ```
   **Checkpoint 3:** the path ends in `.venv`. If it does not, see [Troubleshooting](troubleshooting.md#activation-fails).
7. Install the project with its test tools:
   ```powershell
   python -m pip install -e ".[dev]"
   ```
   Expected shape: `Successfully built raviride-eta` and `Successfully installed ... raviride-eta-0.1.0`.
8. Prove the install is real by importing from a different directory:
   ```powershell
   cd ..
   python -c "import raviride_eta; print(raviride_eta.__file__)"
   cd raviride-eta
   ```
   **Checkpoint 4:** the printed path is your `src/raviride_eta/__init__.py`.

## Part 3: a test that proves the environment works

9. Create `tests/test_smoke.py`:
   ```python
   import raviride_eta


   def test_package_imports():
       assert raviride_eta.__version__ == "0.1.0"
   ```
10. Run it:
    ```powershell
    python -m pytest
    ```
    Expected: one passing test, no errors. If pytest is not found, the `[dev]` extras did not install; rerun step 7 and read its output.
    **Checkpoint 5:** `1 passed`.

## Part 4: repair the colleague's environment

11. Create `colleague/requirements.txt` with exactly:
    ```text
    pandas==1.5.0
    scikit-learn==1.2.2
    jupyter==1.0.0
    ```
12. Try to install it into a throwaway environment so your working one stays intact:
    ```powershell
    python -m venv .venv-colleague
    .\.venv-colleague\Scripts\Activate.ps1
    python -m pip install -r colleague/requirements.txt
    ```
13. Read the failure. You will see either `No matching distribution found for pandas==1.5.0` or a long sdist build failure. Both mean the same thing: no prebuilt package exists for this Python version.
    **Checkpoint 6:** write one sentence in `docs/environment-log.md` naming the interpreter, the package, and the reason - not "it failed".
14. Choose the fix and record why. Recommended: re-create the environment on Python 3.11, which supports those pins. If you only have 3.12, bump to `pandas==2.2.3`, `scikit-learn==1.5.2` and record that this changes behaviour and requires re-verification.
15. Deactivate and remove the throwaway environment:
    ```powershell
    deactivate
    Remove-Item -Recurse -Force .venv-colleague
    ```
    *Recovery:* on bash use `rm -rf .venv-colleague`. Deleting an environment is always safe; it contains no source code.

## Part 5: commit like a colleague will read it

16. Create a branch:
    ```powershell
    git switch -c chore/environment
    ```
17. Stage, then inspect before committing:
    ```powershell
    git add .
    git diff --staged
    ```
    **Checkpoint 7:** the diff contains no `.venv`, no data, no absolute paths, and no credentials.
18. Commit with a message that states the reason:
    ```powershell
    git commit -m "Add package skeleton with pinned environment and smoke test"
    ```
19. Write `docs/environment-log.md`: one row per error you hit - command, exact message, diagnosis, fix. Add the ten-item reproducibility checklist from [Learning objectives](learning-objectives.md) with your score.
20. Export your resolved environment:
    ```powershell
    python -m pip freeze > requirements.lock.txt
    ```
    **Checkpoint 8:** the file exists, has more lines than your direct dependencies (transitives are included), and does not appear in `.gitignore`.
21. Commit the lock file and the log.

## Expected outputs

| Output | What it proves |
|---|---|
| `pyproject.toml` with `requires-python` and bounds | The project declares its own requirements |
| `.venv` that is ignored by Git | Generated state stays out of history |
| `1 passed` from `python -m pytest` | The package imports through the installed path, not the current directory |
| `requirements.lock.txt` | A rebuild is possible without guessing |
| `docs/environment-log.md` with at least one real error | You diagnosed rather than avoided a failure |
| An environment where `python -c "import sys; print(sys.prefix)"` names `.venv` | You can tell which interpreter runs your code |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Isolation | The project installs and tests in its own environment, and the global Python is untouched |
| Reproducibility | A second environment created from `pyproject.toml` + lock installs and passes the smoke test |
| Hygiene | `git status` is clean, and no generated file is tracked |
| Diagnosis | The environment log explains the pandas failure by interpreter version, not by "bad package" |
| Habits | At least one branch and two commits with reason-style messages |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Activate.ps1` cannot be loaded | PowerShell execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then reopen the shell |
| `python` opens the Microsoft Store | Windows app execution alias | Install from python.org, or disable the alias in Settings |
| `ModuleNotFoundError: raviride_eta` after installing | Installed without `-e`, or a different interpreter | Reinstall with `-e`; check `sys.prefix` |
| `No module named pytest` | `[dev]` extras skipped | `python -m pip install -e ".[dev]"` |
| pip tries to build pandas for minutes and fails | No wheel for this Python version | Change Python version or bump the pin; do not use `--no-deps` |
| `fatal: not a git repository` | You are outside the project folder | `cd` into `raviride-eta` |
| Lock file huge and unreadable | It includes every transitive pin | That is correct; keep it, and let a tool like `uv` manage it if you prefer |

## Cleanup

- Delete any throwaway environments: `Remove-Item -Recurse -Force .venv-colleague`.
- Stop any shells still activated with `deactivate`.
- Keep `.venv`, `requirements.lock.txt`, and the log; they are the module's artefacts.

## Optional extensions

1. **Lock with hashes.** Install `pip-tools` or `uv` and produce a lock that includes hashes. Compare the file sizes and explain what the hashes buy you.
2. **Two-version matrix.** Create environments on 3.11 and 3.12, run the tests in both, and record any difference. This is the local version of what Module 12 does in CI.
3. **Break it on purpose.** Rename `src/raviride_eta` to `src/raviride` without changing imports; run the tests; explain the error using the traceback-reading method from [Concepts](concepts.md#8-reading-a-traceback).

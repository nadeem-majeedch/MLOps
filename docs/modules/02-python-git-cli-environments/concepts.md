# Concepts · Module 02

## 1. The interpreter, and which one you are running

A Python installation consists of an interpreter binary, a standard library, and a directory of third-party packages (`site-packages`). When you type `python`, your shell searches the directories in `PATH` in order and runs the first match.

That search is why "which Python am I using?" is a real question with three answers on a typical Windows machine:

| Command you type | What actually runs | When it happens |
|---|---|---|
| `python` | The first `python.exe` on `PATH` | Most of the time; can be a Microsoft Store stub |
| `py -3.12` | The launcher's registered 3.12 interpreter | When you have several versions installed |
| `.\.venv\Scripts\python.exe` | The environment's interpreter, explicitly | In scripts, CI, and when debugging |

The Microsoft Store alias is the classic trap: typing `python` opens the Store instead of running anything. If that happens, install Python from python.org or disable the app execution alias.

**Rule for this course:** know where your interpreter lives. `sys.executable` prints it, and `python -c "import sys; print(sys.prefix)"` prints the environment root.

## 2. Virtual environments: what they isolate

A virtual environment is a directory containing a symlink (or copy) of an interpreter, its own `site-packages`, and its own scripts. It does not copy the standard library or the operating system libraries.

| Isolated per environment | Shared with the machine |
|---|---|
| Third-party packages and their versions | The Python version you created it from |
| Console scripts (`pytest.exe`, `ruff.exe`) | System C libraries, GPU drivers, the OS |
| Which packages `pip install` can see | Your data files, unless you copy them |

That table explains a class of bug that costs teams days: a package with compiled extensions (NumPy, PyTorch) can be installed cleanly and still fail if the system's C++ runtime or GPU driver is wrong. The environment isolates *packages*, not *the machine*.

Two environments, side by side:

```text
raviride-eta/
├── .venv/                     # created by you, ignored by Git
│   ├── Scripts/python.exe
│   └── Lib/site-packages/     # pandas 2.2.3, scikit-learn 1.5.2, ...
└── src/raviride_eta/          # your code, tracked by Git
```

## 3. Activation, and the three ways it fails

Activation does two things: it prepends the environment's script directory to `PATH`, and it sets `VIRTUAL_ENV`. Nothing else changes.

| Shell | Command |
|---|---|
| PowerShell 7 | `.\.venv\Scripts\Activate.ps1` |
| Command Prompt | `.venv\Scripts\activate.bat` |
| Git Bash / Linux / macOS | `source .venv/bin/activate` |

Failures, in order of frequency:

1. **Execution policy.** PowerShell refuses to run `Activate.ps1`: *"running scripts is disabled on this system"*. Fix for the current user: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`. This is a security setting; understand it before changing it.
2. **Wrong shell.** Running `Activate.ps1` from Command Prompt does nothing useful. Match the script to the shell.
3. **The IDE's interpreter.** Activation affects one terminal. VS Code, PyCharm, and Jupyter keep their own interpreter setting, so a notebook can silently use the global Python. Select `.venv\Scripts\python.exe` explicitly.

A fourth, subtler failure: activation succeeded in a terminal, then you opened a new terminal. Each shell session activates separately. If `pytest` suddenly disappears, this is why.

## 4. Dependencies, bounds, and locks

**Direct** dependencies you import. **Transitive** dependencies those packages need. Your project declares the first; pip resolves the second, and the resolution can change when an upstream package publishes a new release.

Three levels of control, weakest to strongest:

| Level | Looks like | Guarantees | Fails when |
|---|---|---|---|
| Loose | `pandas` | Nothing specific | Any release may break you |
| Bounded | `pandas>=2.2,<3` | No major-version surprises | A minor release changes behaviour |
| Locked | Exact versions of every package and hash | The same install tomorrow | The lock is not updated deliberately |

`pyproject.toml` declares bounds. A lock file records the exact resolved set. Both belong in Git; the environment does not.

```toml
[project]
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.2,<3.0",
    "scikit-learn>=1.5,<2.0",
]
```

Upper bounds on major versions are a judgement call, not a universal rule. Libraries that follow semantic versioning deserve them; libraries that do not, need a lock either way. What is not acceptable is an unpinned transitive dependency in a system you must reproduce in six months.

### Locking with pip, honestly

`pip` installs but does not lock by default. The portable approach:

```bash
python -m pip freeze > requirements.lock.txt
```

This records what is installed *now*, including transitives. It is a snapshot, not a solver: to upgrade, change `pyproject.toml`, reinstall, and regenerate. Tools such as `uv`, `pip-tools`, and Poetry produce locks with hashes and conflict resolution; use one if your team already does. The concept to understand is the same: bounds for humans, exact versions for rebuilds.

## 5. Project layout and editable installs

The `src/` layout puts importable code under `src/` instead of the repository root. The reason is test honesty: with a flat layout, `import raviride_eta` can succeed by accident from the current directory, so a broken package still passes locally and fails in CI.

```text
raviride-eta/
├── pyproject.toml
├── src/raviride_eta/__init__.py
├── tests/
└── scripts/
```

An **editable install** (`pip install -e .`) tells Python "this project's package is at this path; use it directly". Edits take effect without reinstalling. The build system reads `pyproject.toml`, which is why the file is configuration rather than documentation.

## 6. Git as a working habit

Git is not a backup tool you use at the end. It is how a change becomes reviewable.

| Command | Question it answers |
|---|---|
| `git status` | Which files changed, which are staged, which are untracked |
| `git diff` | What exactly changed, line by line, in unstaged files |
| `git diff --staged` | What you are about to commit |
| `git log --oneline` | What happened recently, in order |
| `git switch -c fix/zone-lookup` | Start an isolated change |

Three habits separate people who use Git from people who fight it:

- **Commit small and often, on branches.** A commit is a checkpoint you can return to; a branch is a change you can abandon without affecting `main`.
- **Read the diff before you commit.** This is the single highest-value habit in this module. `git diff` catches debugging prints, hard-coded paths, and secrets.
- **Write the message as the reason, not the action.** "Fail the pipeline when a zone is missing" is better than "update validation".

`.gitignore` is part of the design. At minimum: virtual environments, caches, generated data, model binaries, and credentials. A secret that is committed remains in history even after deletion; the fix is rotation, not removal.

## 7. Command-line literacy

Four ideas cover most of what this course uses:

1. **Exit codes.** `0` means success; anything else means failure. Pipelines branch on exit codes, not on log text. Check `$?` (bash) or `$LASTEXITCODE` (PowerShell).
2. **`--help` before guessing.** `python -m pytest --help` answers most questions faster than a search engine.
3. **Composition.** `|` pipes output into another command; `>` writes to a file. `dvc repro 2>&1 | tee repro.log` both shows and records a run.
4. **Paths.** Windows accepts `\` and `/`; forward slashes work everywhere, including in `pyproject.toml` and shell scripts that might later run on Linux.

## 8. Reading a traceback

Python prints the call stack, oldest call first, and the exception last. Beginners read the last line only; that is the *symptom*.

```text
Traceback (most recent call last):
  File "scripts/check.py", line 4, in <module>
    frame = pd.read_csv("data/raw/trips.csv")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../pandas/io/parsers/readers.py", line 1026, in read_csv
    return _read(filepath_or_buffer, kwds)
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'data/raw/trips.csv'
```

Read it in this order:

1. **The exception type and message** (last line): `FileNotFoundError` and the exact path.
2. **The first frame in your own code** (the deepest frame inside *your* files, not the library): here, `scripts/check.py`, line 4. That is where your assumption broke.
3. **The line itself**, shown with a caret marking the failing call.

Then ask: is the path wrong, is the working directory wrong, or does the file genuinely not exist? All three produce the same last line. That question - "which of my assumptions is wrong?" - is the whole skill.

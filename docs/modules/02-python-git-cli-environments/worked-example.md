# Worked example · Building `raviride-eta` from nothing

Every command below was run before it was written here; the output blocks are copied from those runs. Your version numbers may differ, and that is fine as long as the *shape* of the output matches.

## Step 1: confirm the interpreter

```powershell
python --version
```

```text
Python 3.12.10
```

If this opens the Microsoft Store or prints nothing, stop and fix that first (see [Troubleshooting](troubleshooting.md)).

## Step 2: create the repository and the project file

```powershell
mkdir raviride-eta
cd raviride-eta
git init -b main
```

`pyproject.toml` is the only file that needs to exist before installation:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "raviride-eta"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pandas>=2.2,<3.0", "scikit-learn>=1.5,<2.0", "joblib>=1.4", "PyYAML>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0", "ruff>=0.6"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

Two details matter more than they look. `requires-python` states the version you support, so a colleague on 3.9 gets a clear error instead of a confusing syntax failure. `[tool.pytest.ini_options]` means `pytest` needs no arguments to find the tests.

## Step 3: create and activate the environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Your prompt now begins with `(.venv)`. Confirm which interpreter is active:

```powershell
python -c "import sys; print(sys.prefix)"
```

```text
E:\ML-Ops\.venv-verify
```

The path proves the environment is the one being used. If it prints `C:\Users\you\AppData\Local\Programs\Python\Python312`, activation did not take effect in this shell.

## Step 4: install the project

```powershell
python -m pip install -e ".[dev]"
```

```text
Obtaining file:///E:/ML-Ops/raviride-eta
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
Successfully built raviride-eta
Successfully installed PyYAML-6.0.3 raviride-eta-0.1.0
```

The `-e` flag installs in editable mode: Python resolves `raviride_eta` to `src/raviride_eta/`, so edits apply immediately. `".[dev]"` also installs the optional test tools.

## Step 5: verify the import from a fresh shell

```powershell
python -c "import raviride_eta; print(raviride_eta.__version__, raviride_eta.__file__)"
```

```text
0.1.0 E:\ML-Ops\raviride-eta\src\raviride_eta\__init__.py
```

Run this with the current directory *outside* the project. If it only works from inside, the install is not doing its job and your tests will pass locally while failing in CI.

## Step 6: ignore what must not be committed

```text
.venv/
__pycache__/
*.egg-info/
.pytest_cache/
data/raw/
data/processed/
data/features/
models/
mlruns/
metrics.json
baseline.json
```

Then make the first commit on a branch:

```powershell
git switch -c chore/project-skeleton
git add pyproject.toml .gitignore src
git commit -m "Add package skeleton with pinned environment"
```

Before committing, `git diff --staged` should show only those files. If `.venv` appears, `.gitignore` was saved after staging; run `git reset` and stage again.

## Step 7: diagnose a colleague's environment

A teammate sends this `requirements.txt`:

```text
pandas==1.5.0
scikit-learn==1.2.2
jupyter==1.0.0
```

On their Python 3.8 machine it installs. On your Python 3.12 machine:

```text
ERROR: Could not find a version that satisfies the requirement pandas==1.5.0
       (from versions: 2.1.1, 2.1.2, ..., 3.1.0)
ERROR: No matching distribution found for pandas==1.5.0
```

The message is misleading if you read it as "this version is wrong". Nothing is wrong with pandas 1.5.0; it simply has no prebuilt wheel for Python 3.12, and pip will not offer a version it cannot install. Reading the error correctly:

1. The package exists.
2. No build for *this interpreter* exists.
3. Therefore the environment, not the requirement, is the thing that changed.

Two legitimate fixes:

| Fix | When it is right | What it costs |
|---|---|---|
| Create the environment with Python 3.11 | The code genuinely needs the old versions | You now support two Python versions |
| Bump the pins to versions with 3.12 support | The code works on newer libraries | You must re-verify the project, and the lock changes |

The wrong fix is `pip install --no-deps`, which hides the conflict and produces an environment that imports successfully and fails later, usually during training.

This is the "works on my machine" failure in miniature, and it is why the repository - not a colleague's memory - must state the Python version and the dependency bounds.

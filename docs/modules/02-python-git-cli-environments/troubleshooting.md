# Troubleshooting · Module 02

## Activation fails

**`Activate.ps1 cannot be loaded because running scripts is disabled on this system.`**

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then open a new PowerShell window. This permits locally written scripts while keeping downloaded ones signed; it is a security decision, so do not set `Unrestricted` to make a message go away.

**Activation appears to work but `python` is still global.** Check `Get-Command python` and `python -c "import sys; print(sys.prefix)"`. If the prefix is not your `.venv`, the prompt may be stale or a second shell is focused.

**`Activate.ps1` works, then a new terminal loses it.** Expected: activation is per shell session. IDE terminals usually need the interpreter selected in settings, not activation.

**`python` opens the Microsoft Store.** Windows ships an execution alias with no interpreter behind it. Install Python from python.org, then disable Settings → Apps → Advanced app settings → App execution aliases → `python.exe`.

## Installs and imports

| Error | Cause | Fix |
|---|---|---|
| `No module named pytest` | Dev extras not installed | `python -m pip install -e ".[dev]"` |
| `ModuleNotFoundError: raviride_eta` | Not installed, or wrong interpreter | `pip install -e .`; check `sys.prefix` and `raviride_eta.__file__` |
| `No matching distribution found for pandas==1.5.0` | No wheel for this Python | Use 3.11, or bump the pin |
| `ERROR: Could not build wheels for ...` | Source build with missing compiler | Prefer a Python version with a wheel; do not install a compiler just for this |
| `pip` asks for a proxy or times out | Corporate network | Configure `pip config set global.proxy ...`; ask your administrator |
| `PermissionError` writing to `C:\Program Files\...` | Installing into the system Python | Create a venv; never `pip install` as administrator |
| `ImportError: DLL load failed` | Missing system runtime | Reinstall the wheel for the matching architecture; environment isolation does not cover OS libraries |
| `pip check` reports conflicts | A package was force-installed | Rebuild the environment from the lock rather than patching it |

## Editable install installs, but the code does not update

Editable installs resolve to `src/raviride_eta`. If edits do not appear:

1. Confirm `python -c "import raviride_eta; print(raviride_eta.__file__)"` points at your source.
2. Check for a stale `*.egg-info` or `build/` directory and delete it.
3. Reinstall: `python -m pip install -e . --force-reinstall --no-deps`.

## Git

| Symptom | Cause | Fix |
|---|---|---|
| `fatal: not a git repository` | Wrong directory | `cd` to the project root; `git rev-parse --show-toplevel` confirms |
| `.venv` staged for commit | `.gitignore` written after `git add` | `git reset`, verify `.gitignore`, then add again |
| Huge diff with line-ending changes | Windows CRLF versus LF | Add a `.gitattributes` with `* text=auto`, then renormalise |
| Committed a data file | Ignore rules were missing | Remove from the index (`git rm --cached file`), add the rule, commit |
| `git status` shows changes you did not make | Generated files being tracked | Check `git diff` for timestamps or caches; ignore them |

## Long paths on Windows

Deep virtual environments can exceed the legacy 260-character limit. Enable long paths:

```powershell
git config --system core.longpaths true
```

and set the Windows policy `LongPathsEnabled` to 1 (Administrator, Group Policy or registry). If you cannot, keep the project path short, for example `C:\work\raviride-eta`.

## When nothing makes sense

Delete the environment and rebuild from the repository. It takes two minutes and eliminates the most common class of problem:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

If the rebuild succeeds, the environment had drifted. If it fails, the repository is incomplete - which is more useful to know.

# Troubleshooting

Most of the time lost in a self-study course is not spent learning; it is spent fighting an environment. This page collects the problems students actually report, in the order they hit them, with the cause and the smallest fix.

**How to use it:** find your exact message. If it is not here, read the [first five minutes](#0-the-first-five-minutes) section, then the [study problems](#8-when-the-problem-is-not-technical) section - the issue is often not technical at all.

!!! tip "Before changing anything"
    Copy the exact error text into your notes first. Half of all debugging is discovering that the
    message you remembered is not the message you got.

---

## 0. The first five minutes

1. **Read the last line of the traceback.** That is usually the actual error; the lines above are the path to it.
2. **Check which Python and which environment you are in.** Most "module not found" problems are the wrong interpreter.
3. **Check the working directory.** The second most common cause is running a command from the wrong folder.
4. **Re-run the exact command from the lab**, not a version you reconstructed from memory.
5. **If the environment is corrupt, rebuild it.** Ten minutes of rebuilding beats two hours of debugging, and rebuilding is itself the skill this course teaches.

```powershell
# Windows 11 - PowerShell 7 - run from the repository root
python --version
Get-Location
python -c "import sys; print(sys.executable)"
```

Expected result: the version you installed, the folder you expect, and a path inside `.venv`. If the third line points at a system Python, your environment is not active.

---

## 1. PowerShell and Windows

| Symptom | Cause | Fix |
|---|---|---|
| `... cannot be loaded because running scripts is disabled on this system` | Windows blocks `.ps1` scripts by default | Allow scripts for this terminal only: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again |
| Typing `python` opens the Microsoft Store | The Store alias is ahead of your installation on `PATH` | Use `py` instead of `python`, or disable the alias in Settings > Apps > Advanced app settings > App execution aliases |
| `python : The term 'python' is not recognized` | Python is not on `PATH` for this terminal | Close and reopen the terminal; if it persists, reinstall with "Add Python to PATH" checked |
| `Activate.ps1` cannot be found | The virtual environment was never created, or you are in the wrong folder | Check that `.venv\Scripts` exists; recreate with `python -m venv .venv` |
| `&&` is not a valid statement separator | Windows PowerShell 5.1 does not support it | Use PowerShell 7 (`pwsh`), or separate the commands with `;` |
| `curl` prints a PowerShell object instead of a response | `curl` is an alias for `Invoke-WebRequest` | Call `curl.exe` explicitly |
| `The filename or extension is too long` | The legacy path limit (260 characters) | Work in a short path such as `C:\dev\mlops`, or enable long paths (requires administrator rights) |
| A port is already in use | Another process - often an earlier run - holds it | Find and stop it, or choose another port |
| Garbled characters in console output | Code page and UTF-8 mismatch | `chcp 65001`, or set `PYTHONUTF8=1` for the session |

Finding what holds a port:

```powershell
# Windows 11 - PowerShell 7
Get-NetTCPConnection -LocalPort 8000 -State Listen |
  Select-Object LocalAddress, LocalPort, OwningProcess
Get-Process -Id <OwningProcess>
```

Stop it only if you recognise the process. If it is a server you started earlier, stop it from that terminal instead.

---

## 2. Python and packages

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError` although you just installed it | Installed into a different interpreter than the one running | Compare `python -c "import sys; print(sys.executable)"` with the path used by `pip`; activate the environment first |
| `pip` refuses to install globally (`externally-managed-environment`) | A managed Python protects its system packages | Create and activate a virtual environment; never install into the system interpreter |
| Two packages require incompatible versions | Unpinned dependencies resolved differently | Recreate the environment from the lock file; do not "fix" it by upgrading one package at a time |
| `SSL: CERTIFICATE_VERIFY_FAILED` behind a university network | A proxy intercepts TLS | Configure pip's proxy and certificate per your IT guidance; do not disable verification as a habit |
| Warnings about `LF` and `CRLF` from Git | Windows and Unix line endings differ | Set `git config --global core.autocrlf true` on Windows; the warning usually does not break anything |
| A notebook works, a script does not | Different working directory or interpreter | Run the script with the same environment and from the same folder; replace relative paths with paths resolved from the project root |

---

## 3. Docker

| Symptom | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop is not running, or the engine is still starting | Start Docker Desktop and wait for "Engine running" before retrying |
| `WSL 2 installation is incomplete` | WSL 2 is missing or outdated | Follow the WSL documentation; a reboot is usually required after enabling it |
| `virtualization support not detected` | Virtualisation is disabled in firmware, or Hyper-V is unavailable | Enable VT-x/AMD-V in UEFI/BIOS; Docker Desktop cannot work around this |
| The image builds but the container exits immediately | The process inside ended, usually a missing entrypoint or a crash | `docker logs <container>` and run the entrypoint manually to see the error |
| Files created in the container disappear | Container filesystems are ephemeral | Use a volume or bind mount for anything you need to keep |
| The build is slow on every change | Dependencies are copied before source, so the cache is invalidated | Copy dependency files and install first, then copy source |
| Port 5000 is refused on macOS | AirPlay Receiver uses it | Use another port, for example `-p 5001:5000` |

---

## 4. MLflow, DVC, and FastAPI

| Symptom | Cause | Fix |
|---|---|---|
| `mlflow ui` shows no runs | The UI is reading a different tracking location than the runs wrote to | Pass the same store explicitly, for example `mlflow ui --backend-store-uri ./mlruns`, and run it from the project root |
| Runs appear in a new experiment each time | The experiment name is generated or the working directory changed | Set the experiment name explicitly in code |
| `dvc push` fails with "no remote" | No default remote is configured | Add one, for example a local folder, then push |
| `dvc repro` does nothing | Inputs and outputs are unchanged, so the cache is valid | Change an input, or use the documented force option sparingly |
| `dvc checkout` restores the wrong version | The `.dvc` file is from a different commit | Check out the commit first, then `dvc checkout` |
| A prediction endpoint returns 422 | The payload does not match the schema | Read the response body: it names the field and the reason |
| Predictions are plausible but wrong | Serving computes features differently from training | Compare one record through both paths; this is the skew test from Module 10 |

---

## 5. GitHub and CI

| Symptom | Cause | Fix |
|---|---|---|
| A workflow does not run at all | It is not in `.github/workflows/`, or the trigger filters exclude the change | Check the path and the `on:` block; workflows only run when their filters match |
| YAML parsed as a single string | Indentation, usually a tab instead of spaces | Use spaces; validate the file before pushing |
| A step fails only in CI | The runner has a clean environment, unlike your machine | Pin dependencies, avoid absolute paths, and commit every file the pipeline needs |
| Secrets are empty in CI | Secrets are not passed to workflows from forks, and names are case-sensitive | Test on a branch in your own repository; check the secret name |
| The pipeline passes but the model is worse | The gate checks nothing, or the baseline is regenerated by the failing run | Pin the baseline file and make the gate compare against it explicitly |
| Pages or Actions permission errors | The repository's settings do not allow the action | The owner must enable it; a workflow file cannot grant itself permissions |

---

## 6. Data and evaluation

| Symptom | Cause | Fix |
|---|---|---|
| Suspiciously high offline accuracy | Leakage: a feature contains the target or the future | Check each feature for when it becomes known; use a temporal split |
| Metrics change between identical runs | Unseeded randomness, unordered data, or a nondeterministic library path | Fix seeds, sort inputs, pin versions; record all three |
| A "better" model performs worse in use | Selection on the aggregate metric ignored a weak slice | Evaluate per slice before promoting |
| Drift score is extreme on the first batch | Reference and current batches have different schema or units | Align schema first; drift on mismatched columns is meaningless |
| Rows silently disappear after a join | A join key with different types or trailing spaces | Validate row counts before and after every join |

---

## 7. When a lab fights you

**The lab's expected output does not match yours.** Small numeric differences are normal across machines. Compare to the stated tolerance, not to the digit. If the difference is structural - a different number of rows, a different column - stop and find the cause before continuing.

**A step depends on something from an earlier module.** That is by design. Every module page lists its prerequisites; if you skipped one, go back rather than working around it. Modules 05, 07, and 09 punish skipping hardest.

**You cannot install a tool.** Every module has a reduced path, listed in the [tool selection guide](../syllabus/tool-selection-guide.md#7-if-you-cannot-install-a-tool). Reduced paths are honest; record which one you used.

**The lab is too heavy for your machine.** Run one service at a time, close the browser you are not using, and prefer the lighter path. Only Module 16 needs substantially more than 8 GB of RAM.

---

## 8. When the problem is not technical

| Feeling | What is usually happening | What helps |
|---|---|---|
| "I can follow the lab but could not explain it" | Recognition, not recall | Close the page and explain the lab aloud in five sentences; note where you stall |
| "I understand it while reading and lose it by the next day" | Normal forgetting, no retrieval practice | Answer the knowledge check from memory the following day, not immediately |
| "Everyone else seems faster" | You are comparing your first attempt to someone's edited output | Compare your work to the rubric, not to other people |
| "I am three weeks behind" | Compression attempts make it worse | Drop the labelled extensions, keep the essential modules, move the finish date |
| "This feels like too many tools" | Real, and a known risk of the field | Return to the question the tool answers; if you cannot name it, skip the tool |
| "I do not see why this matters" | The business consequence has not landed | Read the failure scenario at the top of the module again; it is written for exactly this |

---

## Still stuck?

Report it with:

1. the page and step number;
2. your operating system and tool versions;
3. the exact command and the exact message;
4. what you expected to happen.

That is enough to reproduce almost any problem. Use the repository's issue tracker.

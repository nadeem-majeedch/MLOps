# References · Module 02

## Official documentation

1. **Python: `venv` - Creation of virtual environments.**
   [docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)
   The authoritative description of what an environment contains. Read the "How venvs work" section, not just the commands.

2. **Python Packaging User Guide: `pyproject.toml`.**
   [packaging.python.org/en/latest/guides/writing-pyproject-toml/](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
   Every field used in this module's `pyproject.toml`, with the tool-specific tables.

3. **pip: Installation and dependency resolution.**
   [pip.pypa.io/en/stable/topics/dependency-resolution/](https://pip.pypa.io/en/stable/topics/dependency-resolution/)
   Explains why the resolver sometimes backtracks and why "no matching distribution" is often an interpreter problem.

4. **pip: `pip freeze` and requirement files.**
   [pip.pypa.io/en/stable/cli/pip_freeze/](https://pip.pypa.io/en/stable/cli/pip_freeze/)
   What a lock snapshot does and does not guarantee.

5. **Git: *Pro Git*, chapters 2 and 3.**
   [git-scm.com/book/en/v2](https://git-scm.com/book/en/v2)
   Branching and merging, free to read. Chapter 2 is enough for this module.

6. **Git: `git diff` documentation.**
   [git-scm.com/docs/git-diff](https://git-scm.com/docs/git-diff)
   The difference between working tree, index, and `HEAD` - the distinction behind `git diff` versus `git diff --staged`.

7. **Microsoft: About Execution Policies.**
   [learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_execution_policies](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)
   Read this before changing the policy, so you know what you are relaxing.

## Optional tools named in the module

8. **`uv` documentation.**
   [docs.astral.sh/uv/](https://docs.astral.sh/uv/)
   A fast installer with its own lock format. The course does not require it; if you use it, keep `pyproject.toml` as the declaration so the standard tools still work.

9. **pip-tools.**
   [pip-tools.readthedocs.io](https://pip-tools.readthedocs.io/)
   Produces a pinned, hashed requirements file from a small input file. Useful when you want locks without changing installer.

## Note on versions

The commands in this module were verified on Python 3.12.10, pip 26.2.2, and Git 2.x on Windows 11 with PowerShell 7. On Linux or macOS the paths differ (`.venv/bin/` instead of `.venv/Scripts/`) but the concepts and commands are the same. Tool documentation is the tie-breaker when a detail differs from this text.

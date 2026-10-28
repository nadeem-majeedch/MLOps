# References · Module 08

1. **DVC documentation: `dvc.yaml` files.**
   [dvc.org/doc/user-guide/project-structure/dvcyaml-files](https://dvc.org/doc/user-guide/project-structure/dvcyaml-files)
   The authoritative definition of `cmd`, `deps`, `params`, `outs`, and `metrics`, including the rule that a stage's outputs are its claim about what it produces.

2. **DVC documentation: `dvc repro`.**
   [dvc.org/doc/command-reference/repro](https://dvc.org/doc/command-reference/repro)
   Read the sections on `--force`, `--single-item`, and `--dry`, and the note that cached outputs are checked out rather than recomputed. The distinction is the heart of this module.

3. **DVC documentation: `dvc status` and `dvc dag`.**
   [dvc.org/doc/command-reference/status](https://dvc.org/doc/command-reference/status) ·
   [dvc.org/doc/command-reference/dag](https://dvc.org/doc/command-reference/dag)
   `status` answers "what is stale, and why"; `dag --mermaid` produces the graph you paste into your evidence file.

4. **DVC documentation: pipeline cache and `dvc gc`.**
   [dvc.org/doc/user-guide/project-structure/internal-files](https://dvc.org/doc/user-guide/project-structure/internal-files)
   Where the cache lives and what a cache entry is. Read before deleting anything to free disk space.

5. **pre-commit documentation.**
   [pre-commit.com](https://pre-commit.com/)
   Installation, the hook lifecycle, and `--no-verify`. Note that hooks are a convenience, not a security control; the same checks belong in CI.

6. **pre-commit-hooks repository.**
   [github.com/pre-commit/pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
   The exact behaviour of `trailing-whitespace`, `end-of-file-fixer`, `check-added-large-files`, and `check-yaml`, including their exit codes.

7. **Python documentation: `subprocess`.**
   [docs.python.org/3/library/subprocess.html](https://docs.python.org/3/library/subprocess.html)
   `check=True`, `capture_output`, and the security note about `shell=True`. The wrapper in this module uses `Popen` to stream output; `run` is sufficient when you only need the result.

8. **Python documentation: `sys.exit` and process exit codes.**
   [docs.python.org/3/library/sys.html#sys.exit](https://docs.python.org/3/library/sys.html#sys.exit)
   Why `raise SystemExit(main())` is the cleanest way to turn a function's return value into an exit code.

9. **Git documentation: Git hooks.**
   [git-scm.com/book/en/v2/Customizing-Git-Git-Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
   What `pre-commit` installs and when it runs. Useful for understanding why hooks are local and can be bypassed.

10. **GNU Make manual: exit status.**
    [gnu.org/software/make/manual/html_node/Errors.html](https://www.gnu.org/software/make/manual/html_node/Errors.html)
    `make` is the older, ubiquitous version of the same idea: targets, prerequisites, and stop-on-error. Reading it makes clear that DVC's semantics are not novel, only better suited to data.

11. **MLflow documentation.**
    [mlflow.org/docs/latest/index.html](https://mlflow.org/docs/latest/index.html)
    Referenced forward rather than used here: Module 09 gives the artefact this pipeline produces a version, an alias, and a promotion gate.

## Note on the numbers

The timings in this module (11.2 s forced, 1.5 s cached, stage durations 0.61–2.10 s) were measured on one laptop CPU with a warm operating-system cache, using `Measure-Command` and `date +%s%N`. The metric values (MAE 2.7686, 2.7874 at 120 trees) come from the reference implementation and the course dataset. Treat the ordering and the DVC decisions as transferable, and the seconds as local.

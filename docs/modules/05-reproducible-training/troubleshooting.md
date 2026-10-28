# Troubleshooting · Module 05

## Caching

| Symptom | Cause | Fix |
|---|---|---|
| A changed file does not trigger a rerun | Not in `deps` | Add it; the cache key only covers declared inputs |
| Every run reruns everything | A dependency changes on every run (log file, timestamp, notebook output) | Remove it from `deps`; write volatile files outside the pipeline |
| Stage skipped but outputs are wrong | Outputs restored from cache from an earlier definition | `dvc repro --force` once, then investigate what was missing from `deps` |
| `dvc.lock` and `dvc.yaml` disagree | Someone edited `dvc.yaml` without repro | Run `dvc repro`; commit both files together |
| Cache grows without bound | Many dataset versions pushed locally | `dvc gc --workspace` prunes unreferenced objects; read the warning first |

## Stage execution

**`ModuleNotFoundError` inside a stage.** DVC runs the command through the shell; the shell resolves `python` from `PATH`. Activate the environment in the same terminal. A second symptom of the same cause: the stage works by hand and fails under `dvc repro`.

**`FileNotFoundError` inside a stage but not by hand.** The stage used a relative path resolved against the current directory. Anchor paths to `config.PROJECT_ROOT`, which is computed from `__file__`.

**Stage succeeds but writes nothing.** Check the output paths: a trailing slash mismatch (`data/processed` versus `data/processed/`) or a directory listed as a file output produces confusing results. DVC expects paths exactly as written.

**`ERROR: failed to reproduce 'evaluate': failed to run: ... exited with 1`.** Read the last lines *above* that error; the real traceback is printed by Python before DVC wraps it.

## Determinism

| Symptom | Cause | Fix |
|---|---|---|
| Metrics differ in the third decimal between runs | Parallel float reduction | `n_jobs=1`; document the drift if you keep parallelism |
| Split membership changes | Row order before splitting, or unseeded split | Sort by a stable key; pass `random_state` |
| Artefact hash differs but predictions match | Pickle ordering or metadata | Compare predictions, not bytes; report which form of determinism you have |
| Feature values differ between batch and single row | Stateful feature function | Move learned statistics into the fitted pipeline |

## Reading DVC output

- `didn't change, skipping` means the cache key matched. It does **not** mean the stage is correct.
- `is cached - skipping run, checking out outputs` means the outputs were missing and were restored from cache. Useful distinction when you deleted a folder to force a rerun.
- `Updating lock file 'dvc.lock'` appears whenever hashes were recomputed; commit the change.

## When the pipeline is slower than the scripts

Measure before optimising. If startup dominates, the cost is DVC's own overhead and there is nothing to fix. If a single stage dominates, that stage is where to look - and now you have the per-stage timings to say so.

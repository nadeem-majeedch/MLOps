# Knowledge check · Module 08

Answer before reading the reasoning. Each question targets a decision you will make in a real pipeline, not a definition you can look up.

## Questions

**1.** A colleague adds `features.py` to the `prepare` stage's `deps` by mistake. What is the cost?

**2.** You change a docstring in `train.py`. DVC reruns `train`. Is that a bug in DVC?

**3.** `dvc repro` prints `Stage 'train' is cached - skipping run, checking out outputs`. Did the model improve, regress, or neither?

**4.** A wrapper calls `subprocess.run(["dvc", "repro"])` and does not inspect the return value. What can go wrong downstream, and what is the smallest fix?

**5.** Why does the reference wrapper use exit code `2` for preflight failures instead of `1`?

**6.** `metrics.json` is written at the start of the evaluate stage, then the stage computes slices and crashes. Why is failing *after* writing the file worse than failing before?

**7.** Two engineers run `dvc repro` on different branches and both commit `dvc.lock`. The merge conflicts. What is the correct resolution?

**8.** A stage takes 40 seconds and runs on every commit via `pre-commit`. What is wrong with that design, and where should the check go instead?

**9.** Your pipeline's cached run takes 1.5 s and a forced run 11 s. A manager asks why the nightly job takes 11 s. Give the accurate answer in one sentence.

**10.** You add a new stage that trains a model per zone and a final stage that combines the metrics. The combine stage averages whichever metric files exist. Name the failure mode this creates and the smallest change that prevents it.

---

## Answers and reasoning

**1.** `prepare` reruns whenever `features.py` changes. Cost: wasted compute and a misleading graph, but the result is still correct. Over-declaring is *visible* waste; under-declaring is invisible wrongness. This asymmetry is why the guidance is "when unsure, declare".

**2.** No. The cache key includes the command and the content of declared dependencies, and `train.py` is one of them. A comment change alters the file hash, so the stage is considered stale. DVC hashes bytes, not meaning; it cannot know that a comment does not affect behaviour, and pretending otherwise would require parsing Python. Over-invalidating is the safe direction.

**3.** Neither. The outputs are byte-identical to a previous run with the same key; they were copied from the cache. "Cached" answers "is this the artefact these inputs produce?", not "is it good?". Quality is Module 06 and 09's job.

**4.** The wrapper reports success even when a stage failed, so a scheduler, CI job, or colleague proceeds with stale artefacts. Smallest fix: `subprocess.run([...], check=True)` or test `returncode` and propagate it. `check=True` raises `CalledProcessError`, which the wrapper should translate to its own non-zero exit.

**5.** Because the two failures have different owners and different remedies. `2` means the environment or inputs are wrong — missing file, wrong interpreter, unparsable params — and the fix is usually outside the pipeline code. `1` means the pipeline ran and a stage failed, which the ML engineer owns. A scheduler can route alerts on that distinction without parsing text.

**6.** A file that exists but is incomplete is indistinguishable from a valid result to everything downstream: the regression gate reads it, CI uploads it, a dashboard plots it. Writing early converts "the stage failed" into "the pipeline produced a plausible but wrong number". Compute every value first, then write once — ideally to a temporary file and rename.

**7.** Do not merge hashes. Check out the merged `dvc.yaml` and `params.yaml`, run `dvc repro`, and commit the regenerated `dvc.lock`. The lock file records what the current declaration produces; hand-editing it makes the record disagree with reality, which is worse than a longer merge.

**8.** A 40-second hook taxes every commit, including the trivial ones, so people start using `--no-verify` and the hook stops protecting anything. Commit hooks should be fast and local (whitespace, YAML validity, file size, a quick unit subset). Slower checks belong in CI, where their cost is paid once per push and cannot be bypassed.

**9.** "The cached run proves nothing changed; the nightly job deliberately recomputes everything so a cache or environment problem cannot hide a broken pipeline." The 11 s is the cost of verification, not of training.

**10.** Partial success is silently averaged: the combined metric looks valid while representing fewer zones, so a zone that failed to train disappears from the report instead of blocking the release. Smallest fix: the combine stage asserts that every expected zone file exists and fails when one is missing. Better: make the expected set explicit in `params.yaml` so a new zone cannot be forgotten.

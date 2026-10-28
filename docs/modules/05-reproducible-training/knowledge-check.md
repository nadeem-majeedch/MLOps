# Knowledge check · Module 05

## Questions

1. Distinguish deterministic, reproducible, and replicable in one sentence each.
2. Name four sources of nondeterminism in a training run and one control for each.
3. What four things make up a DVC stage cache key?
4. You change `model.max_depth`. Which stages rerun, and why do the others not?
5. What is a "hidden input", and how does it manifest as a symptom?
6. Why should a feature function be stateless, and what breaks if it is not?
7. A stage appends a line to `metrics.jsonl` on each run. Why is this a problem for a pipeline, and what should replace it?
8. What does `cache: false` on a metrics file change?
9. Why compare against a constant baseline before celebrating a model's MAE?
10. Two runs produce identical metrics but different model hashes. Is the pipeline deterministic? Explain.

## Answers and reasoning

**1.** Deterministic: same inputs produce the same output on the same machine. Reproducible: another person with the same code, data, parameters, and environment obtains the same result. Replicable: another person with independent data drawn from the same process reaches the same conclusion.

**2.** Unseeded randomness (pass a seed from params); hash/set iteration order (sort explicitly); parallel float reduction (`n_jobs=1` or accept drift); wall-clock time in features or filenames (inject a fixed value); environment differences (pin versions and record them); unsorted file discovery (sort paths).

**3.** The command string, the hashes of declared dependencies, the values of declared parameters, and the hashes of the outputs.

**4.** `train` and `evaluate`. `train` declares `model` in `params`; `evaluate` depends on the model artefact. `prepare` and `featurise` do not declare that parameter and their inputs did not change, so their keys are unchanged.

**5.** A file or value the stage reads but does not declare, so it can change without invalidating the cache. Symptom: results look stale after a change; the stage "did not change, skipping" while its real input did. Diagnosis: compare the declared `deps` with the imports and file reads in the stage.

**6.** Because serving calls it on a single row, where any batch-level statistic (mean fill, group normalisation, ranking) is undefined or different. The practical break: features computed at serving differ from training even though the code is "the same", which is training/serving skew.

**7.** The output depends on how many times the stage ran, not only on its inputs, so the stage is not idempotent and the cache key cannot describe it. Replace it with a tracker that records runs as separate entities (Module 06), or write a single file that is fully rewritten.

**8.** It keeps the metrics file outside DVC's cache, so it is written as a normal file and can be committed and diffed in Git. Hashing it into the cache would hide the values from review.

**9.** To catch a pipeline that is silently wrong: if a random forest loses to "predict the median", the likely cause is a data or feature bug, not model capacity. The baseline is a sanity check with a known value.

**10.** Deterministic in behaviour, not necessarily in bytes: identical metrics and (usually) identical predictions, but pickled objects can differ in ordering, floating-point representation, or embedded metadata. The honest claim is "deterministic predictions, artefact bytes may differ", and the report should say which was observed.

## Scoring

| Score | Next step |
|---|---|
| 8–10 | Continue to Module 06 |
| 5–7 | Reread sections 2–4 of [Concepts](concepts.md) and redo the lab's Part 3 |
| 0–4 | Rebuild the pipeline from the worked example before continuing; every later module assumes it |

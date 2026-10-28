# Independent challenge · Halve the runtime without changing the answer

## The brief

Your pipeline takes about 11 seconds from a forced run. The team retrains twice a week and the data team reruns it far more often while investigating. Make the *common* case fast, prove the result did not change, and be honest about which part you did not speed up.

"Halve the runtime" is deliberately ambiguous. You must decide which runtime:

- the forced full run (what CI does),
- the cached run (what you do twenty times an hour),
- or the loop from "I changed one parameter" to "I have a new metric" (what experiments actually need).

Pick one, state it, and measure it. A claim without a stated baseline is not a result.

## Constraints

- The metric must not change. Same `metrics.json` values, byte-for-byte where possible.
- No changing the model to something cheaper. This is an engineering exercise, not a modelling one.
- No removing validation or tests to buy time.
- No new paid service and no cloud account.
- The change must survive `dvc repro --force` on a clean checkout.

## Suggested directions

Choose one or two; do not do all of them.

| Direction | Idea | Risk to watch |
|---|---|---|
| Parallelism | Train per-zone models in parallel, or fit with `n_jobs=-1` | Timing changes; determinism may not |
| Fewer reruns | Add a stage between `featurise` and `train` so parameter changes skip feature work | More stages, more declarations to get wrong |
| DVC overhead | Replace `dvc repro` with a direct call for the cached path | Loses the cache; must not become the documented default |
| Data volume | Train on a stratified subsample | **Changes the metric** — only allowed if you show it does not |
| Interpreter start-up | Import only what the stage needs; avoid heavy imports in `__init__` | Small gains; measure before claiming |

## What to submit

1. **A baseline measurement.** Three runs, median, method stated, machine named. A single run is not a measurement.
2. **The change**, with the diff and a one-paragraph justification.
3. **The equivalence proof.** For the same inputs, the metric before and after, plus the output hashes (for example SHA-256 of `metrics.json` and `models/model.joblib`). If the artefact hash changes but the metrics do not, say so and explain why that is acceptable or not.
4. **The new measurement**, same method as the baseline.
5. **A short "what I did not speed up" section.** Every pipeline has a floor; name yours.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Baseline | Measured, repeated, and reported with a method |
| Claim | A specific runtime is halved, not "the pipeline is faster" |
| Equivalence | Metrics identical; artefact differences explained |
| Reproducibility | The change works from `dvc repro --force` on a fresh clone |
| Honesty | The floor is named, including DVC's start-up cost if it dominates |
| Safety | Validation, tests, and declarations still run |

## Reference observation

On the reference machine, the four stages total 4.9 s while the whole `dvc repro` takes 11.2 s. Roughly 6 s is DVC's own overhead. This is a hint and a warning: halving *stage* time at this scale changes the total by less than a quarter. If your baseline includes DVC, you must attack the overhead or change the common path; if it excludes DVC, say so explicitly.

## Stretch

Measure the loop a colleague actually uses: edit a parameter, run, read the metric. Instrument it with timestamps (shell history is enough), repeat five times, and report the median. Then optimise *that*, and explain why the number differs from `dvc repro`'s wall time.

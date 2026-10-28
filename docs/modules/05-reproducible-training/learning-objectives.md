# Learning objectives · Module 05

| # | Objective | Evidence |
|---|---|---|
| 1 | Make training deterministic | Same data, code, and parameters produce identical metrics and an identical artefact hash |
| 2 | Separate feature logic for reuse | One transformer used by training and by a single-row prediction path |
| 3 | Declare stages with inputs, outputs, and parameters | `dvc.yaml` with four stages; no hidden file reads |
| 4 | Predict cache behaviour | Before running, state which stages will execute after a given change |
| 5 | Explain invalidation | A table of change → affected stages, confirmed by a real run |
| 6 | Measure stage cost | Per-stage wall-clock timings recorded for a fresh run |

## The reproducibility evidence list

A claim of reproducibility needs all six:

- [ ] The command that produced the result is recorded (not remembered).
- [ ] The dataset is identified by hash (Module 04).
- [ ] Parameters are in a file, and that file is in Git.
- [ ] Seeds are set for every stochastic step, including the split.
- [ ] The environment is pinned (Module 02).
- [ ] Two clean runs produce byte-identical metrics, and ideally a byte-identical artefact.

"Byte-identical artefact" is the strong form. Some libraries embed timestamps or nondeterministic ordering, in which case the honest claim is "identical metrics and predictions", and the difference is documented.

## Self-check before you start

You should know scikit-learn `Pipeline` and `ColumnTransformer` well enough to read one. If not, work through the scikit-learn "Pipelines and composite estimators" page first; this module uses them, it does not teach them.

After the module, you can answer:

1. What is the difference between reproducible and replicable?
2. What is in a cache key, and what is deliberately not?
3. Why does changing `max_depth` not rerun `prepare`?
4. Why can two runs with the same seed still differ?
5. Where should a feature be computed so that training and serving agree?

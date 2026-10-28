# Independent challenge · Prove reproducibility, then find what defeats it

**Time:** 3 hours. **Deliverable:** `docs/reproducibility-report.md`.

The lab asserted determinism twice on one machine. That is necessary and not sufficient: the claim you will need to make in a review is *"someone else can rebuild this and get the same result"*.

## Part A: the two-run report

1. From a clean cache and a clean checkout, run the pipeline twice. For each run record:
   - `git rev-parse --short HEAD`
   - the `data/raw/trips.csv` md5
   - `params.yaml` contents (or its hash)
   - the metrics file, byte for byte
   - the artefact's SHA-256
   - wall-clock time per stage
2. Present the comparison as a table with a `same/different` column.
3. State your conclusion in one sentence, using the precise term: deterministic, reproducible, or both.

## Part B: break it on purpose

4. Introduce, one at a time, two sources of nondeterminism from the [Concepts](concepts.md#where-nondeterminism-comes-from) table. Suggestions: remove `random_state`, set `n_jobs=-1`, or shuffle before splitting without a fixed seed.
5. After each change, run twice and record what differed: metrics, artefact hash, or both.
6. Restore determinism after each experiment and confirm the hashes return.
7. **Most important step:** explain why the *metrics* can stay identical while the artefact hash changes. A model can be equivalent in predictions and different in bytes; both facts matter, for different reasons.

## Part C: the honest limitations paragraph

8. Write one paragraph titled "What this pipeline does not guarantee". Cover at least:
   - floating-point differences across CPUs or BLAS builds;
   - library patch versions (pinned, but a rebuild may fetch a different wheel for a new OS);
   - data drift after the run (reproducing yesterday's model is not producing today's correct one);
   - the model's correctness rather than its reproducibility.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Evidence | Both runs have all six recorded fields, from real commands |
| Precision | The conclusion distinguishes deterministic from reproducible |
| Diagnosis | The identical-metrics/different-bytes case is explained mechanistically |
| Honesty | The limitations paragraph names four concrete limits, not "results may vary" |

## Extension

Add a `dvc metrics diff` comparison between two commits (`git checkout` the earlier one, run, compare) and include the command output. Explain what it shows that a manual diff of `metrics.json` does not.

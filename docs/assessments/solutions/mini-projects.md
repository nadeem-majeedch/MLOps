# Mini-project reference notes

> **Reference only.** These notes describe one design that meets the briefs and
> was executed. They are not the only correct answer, and reading them before a
> first attempt removes most of the learning. The briefs are in
> [mini-projects](../../projects/mini-projects/index.md).

The working code these notes refer to lives in
[`examples/raviride`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/raviride) and
[`examples/starters`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/starters). Read the notes, then the code,
then decide where you would diverge.

---

## MP1 · Reproducible training package

**Design decisions worth copying**

- Four stages, one output each: `prepare`, `featurise`, `train`, `evaluate`.
  Splitting at output boundaries, not at function boundaries, is what makes the
  cache useful.
- `params.yaml` holds the seed, split fraction, and model parameters. Every stage
  declares only what it reads, which is why changing `max_depth` reruns train and
  evaluate but not prepare.
- The dataset is a `.dvc` pointer; the manifest records supplier, date, rows, and
  hash. The repository never carries the CSV.
- `metrics.json` is `cache: false`, so the values appear in a diff.

**The wrong turn most submissions take**

Splitting the code into modules but keeping one stage. It looks organised and
gives none of the cache behaviour the brief asks for. The test is `dvc repro`
after a parameter change: if every stage reruns, the graph is decorative.

**What the evidence looks like**

Two `metrics.json` files from two clean clones, the stage log after a parameter
change, and one broken run with its error. The broken run is the part students
delete; keep it.

---

## MP2 · Evaluated and registered model

**Design decisions worth copying**

- The selection rule is a file with a date, committed before the runs. It names
  the metric, the slice constraint, and the tie-break.
- The gate is a script returning non-zero, called by a command. The registry is a
  consequence of the gate, not a separate ceremony.
- The baseline is pinned by run ID and hash. A regenerated baseline is the most
  common reason a gate passes a bad model.
- Rollback is a timed drill with `/model-info` as proof, not a claim.

**The wrong turn**

Optimising the aggregate, then discovering the regression in the capstone. The
brief asks for a named slice where the winner is worse; if your winner is better
everywhere, your slices are too coarse.

**Reference numbers from the course project**

The candidate blocked in the module lab fails on the `noz08` slice despite a
better aggregate. That is the shape to reproduce: a plausible model, a real
improvement, and a specific reason it cannot ship.

---

## MP3 · Served, containerised, gated service

**Design decisions worth copying**

- One `feature_frame()` function imported by training and serving. The contract
  test calls both on the same row; comparing against a second hard-coded list
  tests nothing.
- The request model forbids extra fields. This is the difference between an error
  and a silently ignored field.
- The Dockerfile installs dependencies before copying source, runs as a non-root
  user, and bakes the artifact in. The artifact hash is reported at
  `/model-info`.
- The CI gate reads a pinned baseline file and compares the new metric; it does not
  re-run the baseline.

**The wrong turn**

A 200 response with a defaulted value for a missing field. It makes every
malformed-payload test pass and teaches the client that the field is optional.
Reject, do not default.

**Limitation to state**

If Docker is unavailable, the container is untested. The brief's honesty criterion
covers that; claiming a build you did not run does not.

---

## MP4 · Monitored lifecycle

**Design decisions worth copying**

- A frozen reference built from the training window, hashed and stored. Rolling
  references hide slow drift.
- Per-feature PSI with a minimum batch size, and an alert that requires two
  consecutive breaches. The control batches are reported alongside the shifted
  one.
- The report separates input drift, prediction drift, and outcome metrics. It
  never says "accuracy fell" without labels.
- Retraining opens a candidate; the MP2 gate still decides promotion.

**The wrong turn**

Choosing a strict threshold to look rigorous, then alerting on every batch. An
alert that always fires is equivalent to no alert and is worse for morale.

**What to show**

Four batches: three controls and one shifted. The alert fires once. If it fires
three times, the threshold is wrong, not the data.

---

## MP5 · Operate and hand over

**Design decisions worth copying**

- The runbook is written from shell history, then tested on a person. The questions
  that person had to answer alone become the findings.
- Retries are enabled only after the task is idempotent. The backfill is verified
  by row counts and a natural key.
- The threat model names residual risk; a list of mitigations without it is a
  wish.
- Capacity is arithmetic from a measured per-pod throughput, with the assumption
  that could be wrong stated.

**The wrong turn**

Writing a runbook that describes the architecture rather than the procedure.
"Deploy the service" is not a step; the command, the expected output, and the
failure response are.

**Limitation to state**

If no second person is available, wait 48 hours and follow your own runbook with
the repository closed. Say that this is what you did; it is weaker evidence, and
the rubric's top band reflects that.

---

## How these notes were verified

| Claim | Verification |
|---|---|
| Starter projects run | `python examples/starters/verify_starters.py`, 12/12 checks |
| Advanced drift and gate | `cli.py all`: train, promote, then exit 2 on drift |
| Intermediate service | Tests plus live HTTP requests to `/health`, `/ready`, `/predict` |
| Docker instructions | Not executed; the environment had no Docker |
| CI workflow | Commands executed locally; no hosted run |

If your run differs structurally — a missing key, a wrong exit code — treat it as
a defect before treating it as tolerance. Numeric metrics may differ by a few
hundredths between library versions; a status code may not.

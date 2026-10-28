# MP1 · Reproducible training package

| | |
|---|---|
| **After** | [Module 05](../../modules/05-reproducible-training/index.md) |
| **Integrates** | Modules 02–05 |
| **Effort** | About 8 hours |
| **Weight** | 10% (illustrative) |
| **Evidence** | A clean clone, two runs, one comparison |

---

## Brief

A colleague clones your repository on a different machine and must obtain your
reported metric without asking you anything. That is the whole requirement. It
sounds modest and it is where most projects fail: the data is in a chat message,
the environment is `pip install` of whatever was current, the seed is in a
notebook cell that was run twice, and the "reported metric" came from a run whose
data no longer exists.

You are not being asked for a perfect pipeline. You are being asked for one that
a stranger can execute and trust.

---

## Deliverables

1. **Repository** with a pinned environment and one documented install command.
2. **Versioned dataset** with provenance: where it came from, when, its hash, and
   how to obtain it.
3. **Stage graph** for prepare, featurise, train, evaluate, with declared inputs
   and outputs.
4. **`metrics.json`** plus a two-run comparison showing agreement within a
   tolerance you stated in advance.
5. **A README section** a stranger can follow, including the expected metric and
   its tolerance.
6. **One deliberately broken run**, documented: the change, the symptom, and the
   fix.

Keep the artefact names stable: `dvc.yaml`, `params.yaml`, `metrics.json`,
`data/`, `models/`. Later mini-projects assume them.

---

## Acceptance criteria

A stranger with the repository and a machine can check all of these:

- [ ] A clean directory installs and trains using only commands in the README.
- [ ] Two clean runs agree within the stated tolerance, and the tolerance is
      written in the README *before* the results.
- [ ] Changing one hyperparameter invalidates only the stages that declare it,
      shown by the stage log.
- [ ] The dataset version is identified by a hash or tag, and the repository does
      not contain the dataset itself.
- [ ] No absolute paths, no credentials, no untracked file is required for the run.
- [ ] `git status` is clean after a fresh run, apart from ignored outputs.
- [ ] The deliberately broken run is described with its real error message.

---

## Evidence

| Claim | Weak | Strong |
|---|---|---|
| Reproducible | "Works on my machine" | A clean clone in a new directory, a pasted command sequence, and the metric from that clone |
| Same result twice | "Ran it twice" | Two `metrics.json` files with hashes, and a diff of the metric values |
| Only affected stages rerun | "DVC handles it" | The stage log showing `skipped` for prepare/featurise and `ran` for train/evaluate |
| Data versioned | "It is in DVC" | The `.dvc` file, the remote or cache location, and the hash that resolves |

---

## Rubric

Four criteria, each 0–3. Multiply by two for a total out of 24, then scale to 10.

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Clean-clone reproducibility** | Does not run | Runs with undocumented steps | Runs from the README; metric within tolerance | As level 2, plus a second machine or fresh directory results compared |
| **Data provenance** | No record | A path and a date | Versioned with a hash and retrieval instructions | As level 2, plus a manifest tying rows, columns, and hash to the run |
| **Pipeline structure** | One script | Stages exist but dependencies incomplete | Declared deps, params, and outputs; correct invalidation | As level 2, plus a demonstrated undeclared-input defect and its fix |
| **Honesty** | Claims without evidence | Some evidence, gaps unstated | Every claim has evidence | As level 2, plus stated limitations and one thing not attempted |

A submission that cannot be reproduced is capped at 1 on the first criterion no
matter how good the code is. That is the gate, not a preference.

---

## Build order

1. Freeze the environment; write the install command; test it in a new directory.
2. Move data acquisition into a documented step; hash the input.
3. Split the script into four stages, one output each.
4. Add `params.yaml` and declare what each stage reads.
5. Run twice from cold; record both metrics.
6. Break one declaration; capture the stale result; fix it.
7. Write the README from the audit log, not from memory.

Steps 1–3 are most of the work. If you are interrupted after step 4, you still
have something assessable.

---

## Common failures

| Failure | Signature | Fix |
|---|---|---|
| Untracked file in the working directory | Clean clone gives a different metric | Clone to a new folder before every submission |
| Seed set in one place only | Two runs differ slightly | Pass the seed from params into every random call |
| Absolute path in a config | Works for you, fails for the marker | Resolve paths relative to the project root |
| Dataset committed "just in case" | Repository size grows; hash never matches | Version it, exclude it, document retrieval |
| Tolerance chosen after the run | Suspiciously round number | Write it before: "within 0.02 MAE" |
| Metrics appended per run | File grows; stage never reproduces | Write one file per run, or use a tracker |

---

## Extension

Replace the synthetic dataset with an openly licensed one and document licence,
provenance, and sensitivity in the README. The [datasets guide](https://github.com/nadeem-majeedch/MLOps/blob/main/datasets/README.md)
lists sources and the four questions to answer before substituting.

See also: [Lab 04 · Version and reproduce](../../labs/lab-04-version-and-reproduce.md),
[Lab 05 · Deterministic pipeline](../../labs/lab-05-deterministic-pipeline.md), and
the [beginner starter](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/starters/beginner-support-risk)
for a working project shape.

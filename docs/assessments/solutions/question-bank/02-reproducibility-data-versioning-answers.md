# Answer key · Question bank 02

[Back to the questions](../../question-bank/02-reproducibility-data-versioning.md)

---

## Section A (1 mark each)

**A1 — a.** Command, dependency hashes, declared parameter values, output hashes.
Timestamps and commit hashes are not inputs to the computation, so they cannot be
part of a cache key; if they were, every commit would invalidate everything.

**A2 — b.** A `.dvc` file is a pointer: md5, size, and path in the cache/remote.
You need access to the remote (or the cache) and the revision that contains the
matching `.dvc` file. It is recoverable if the remote retains it; (c) overstates.

**A3 — b.** Unseeded shuffling changes the result between runs on the same
machine, so the run is not deterministic. It can still be reproducible if the
seed is recorded and replayed — but as written it is neither. Changing a
hyperparameter (a) or data (c) changes the result *by design*; both are
reproducible if recorded.

**A4 — b.** DVC only knows what the stage declares. An undeclared file can change
without invalidating the cache. Fix: add it to `deps`, not disable caching — that
would only hide the problem more slowly.

## Section B (3 marks each)

**B1.** Reproducible: another person with the same code, data, parameters, and
environment obtains the same result. Replicable: an independent study with new
data from the same process reaches the same conclusion. A course project can
claim reproducibility, demonstrated by a clean clone; it cannot claim
replicability, because the dataset is synthetic and the sampling process is
invented. Full marks require the distinction and the honest limit.

**B2.** A cached metrics file is stored by content hash and not written to the
working tree in the usual way, so it cannot be reviewed or diffed; worse, a stage
whose output depends on how many times it ran is not a function of its inputs. In
practice the values disappear from the pull request, where the reviewer needs
them. `cache: false` keeps it as a normal file.

**B3.** Any two decisions with a reason:

- *Immutability*: each delivery is stored under a content hash and never
  overwritten; the "latest" pointer is separate.
- *Validation before versioning*: a batch that fails schema checks is quarantined
  and does not become a version, so bad data cannot be cited as a baseline.
- *Provenance*: record supplier, delivery date, row count, and hash in a manifest.
- *Retention*: how many weeks stay available, and where the archive lives.
- *Lineage*: which dataset version each model version used.

## Section C (4 marks each)

**C1.** The claim is too strong. Identical metrics show **behavioural**
determinism — the predictions agree. Different bytes can come from pickle
ordering, embedded library metadata, or float representation. Report:
"deterministic predictions; artifact bytes differ, and here is the evidence." If
the hash is used as a release identifier, hash the *predictions* or the model
parameters, not the pickle.

Marks: 1 for rejecting the claim; 1 for behavioural vs byte determinism; 1 for a
concrete cause; 1 for the practical recommendation.

**C2.** Candidates and checks:

| Source | Check |
|---|---|
| Dependency versions (BLAS, NumPy, scikit-learn) | Compare `pip freeze` or the lock file on both machines |
| Thread count / parallel reduction order | Set `OMP_NUM_THREADS=1`, `n_jobs=1`; compare again |
| Locale, timezone, or default encoding | Run with `LC_ALL=C`, `TZ=UTC`, `PYTHONUTF8=1` |
| CPU architecture and floating-point behaviour | Compare intermediate arrays or per-row predictions, not only the aggregate |
| A hidden file (`.env`, local config) | List files read during the run; compare working trees |

Accept any three with a check. One mark per pair.

## Section D (9 marks)

A strong answer separates four stores and one record:

| Element | Marks | What it looks like |
|---|---|---|
| Immutable raw delivery | 2 | Each Monday's file stored under `raw/2026-10-26/<sha256>.csv`, never edited; a manifest with supplier, time, rows, hash |
| Derived, reproducible data | 2 | Cleaning and feature code versioned with the repo; derived datasets rebuildable from raw + code, and hashed when produced |
| Manual fixes as code | 2 | A hand fix becomes a reviewed patch or a scripted correction with a reason, not an edit to the raw file; the patch is versioned and applied in the pipeline |
| Environment and run record | 2 | Locked environment, container image digest; each run records data hashes, code commit, parameters, and image digest |
| Audit and access | 1 | Retention policy, who can read raw data, and a retrieval procedure tested once (restore an old version) |

Lose a mark for storing weekly files by name only (`latest.csv`), for allowing
hand edits to raw data, or for claiming Git can hold 2 GB files without a remote
or DVC. The auditor requirement is the test: can you name every input to a model
from six months ago, including the fix someone made by hand?

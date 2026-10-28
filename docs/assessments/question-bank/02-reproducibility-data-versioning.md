# Question bank 02 · Reproducibility and data versioning

| | |
|---|---|
| **Covers** | [Module 02](../../modules/02-python-git-cli-environments/index.md), [Module 04](../../modules/04-data-quality-versioning/index.md), [Module 05](../../modules/05-reproducible-training/index.md) |
| **Level** | Foundation |
| **Questions** | 10 |
| **Marks** | 30 |
| **Time** | 40 minutes |
| **Answer key** | [02 · Answers](../solutions/question-bank/02-reproducibility-data-versioning-answers.md) |

---

## Section A · Multiple choice (4 marks)

**A1.** A DVC stage's cache key is built from which four things?

- a) The command, dependency hashes, parameter values, and output hashes
- b) The commit hash, the branch, the author, and the timestamp
- c) The Python version, the OS, the CPU count, and the seed
- d) The command, the working directory, the log file, and the outputs

**A2.** A colleague sends you `data/trips.csv.dvc` with no data file. What can
you conclude?

- a) The data is in Git LFS
- b) The file records a hash and a remote location; you need the remote and the
  right revision
- c) The data was deleted and cannot be recovered
- d) The `.dvc` file is enough to train

**A3.** Which change makes a training script *non-deterministic* while leaving it
reproducible?

- a) Changing `max_depth`
- b) Shuffling rows with an unseeded random generator
- c) Using a different dataset version
- d) Upgrading scikit-learn

**A4.** A pipeline says `Stage 'featurise' did not change, skipping`, but you
edited a lookup table that the stage reads. What is the defect?

- a) The cache is corrupted
- b) The lookup table is an undeclared dependency
- c) DVC cannot track CSV files
- d) The stage needs `cache: false`

---

## Section B · Short answer (9 marks)

**B1.** *(3 marks)* Distinguish **reproducible** from **replicable**, and say
which one a course project can honestly claim.

**B2.** *(3 marks)* Why should a metrics file be excluded from a stage's cache
(`cache: false`), and what goes wrong if it is cached?

**B3.** *(3 marks)* Your dataset is updated weekly by a supplier. Describe two
versioning decisions you must make before the first update arrives.

---

## Section C · Debugging and diagnosis (8 marks)

**C1.** *(4 marks)* Two runs on the same machine produce identical metrics but
different `model.joblib` hashes. A colleague says the pipeline is therefore not
reproducible. Is the claim correct? What would you report?

**C2.** *(4 marks)* A run reproduces an old metric exactly on your laptop, but a
colleague on Linux gets a different value. The data hash matches and the code
commit matches. Name three remaining sources of difference and one check for
each.

---

## Section D · Architecture and scenario (9 marks)

**D1.** Design the data and environment versioning for a project where:

- a supplier delivers a 2 GB CSV every Monday;
- analysts sometimes fix a bad row by hand;
- two people train models on the same server;
- an auditor must be able to reconstruct any model from six months ago.

State what is stored, what is derived, what is immutable, and how a training run
records its inputs. *(9 marks)*

# 04 · Data quality, validation, and data versioning

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 14 hours | [02](../02-python-git-cli-environments/index.md), [03](../03-project-organization/index.md) | Essential |

The ETA model's quality is now determined mostly by its data, and the pipeline accepts any CSV it is given. This module makes that unacceptable: eight executable checks that fail loudly, a test that catches leakage, and a versioning scheme that ties a model to the exact bytes it learned from.

Version control comes first in this course and data versioning second, deliberately. DVC is easier to understand once you know what Git does and does not store.

## What you will be able to do

- Write explicit expectations for schema, ranges, uniqueness, domains, time, and cross-field consistency.
- Implement them so a corrupt batch stops the pipeline with a message that names the rows.
- Version a dataset so any training run can be tied to a specific state of it.
- Detect temporal leakage and explain why a random split hides it.
- Document provenance, licence, and known limitations.

## Start here

1. Read [Concepts](concepts.md) sections 1–4. Section 4 is the one that changes how you evaluate models.
2. Run the [worked example](worked-example.md) against the corrupt batch to see a real failure report.
3. Do the [lab](lab.md): eight checks, one deliberately bad batch, then DVC.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the data-quality review checklist |
| [Concepts](concepts.md) | Contracts, check types, leakage, provenance, DVC |
| [Worked example](worked-example.md) | One check written three ways, and a real failure report |
| [Guided lab](lab.md) | Eight checks, a rejected batch, DVC tracking, a leakage test |
| [Independent challenge](independent-challenge.md) | Prove a leaky feature, then document provenance |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | DVC, remote, and validation failures |
| [References](references.md) | DVC, pandera, and leakage sources |

## What you produce

- `src/raviride_eta/data.py` with eight named checks and a readable report.
- A recorded pass and a recorded failure, both from real runs.
- `data/raw/trips.csv.dvc`, a configured local remote, and a restore you performed.
- `data/README.md` with provenance, licence, and limitations.
- A leakage note explaining what would invalidate the current model.

## Next

[Module 05 · Reproducible training](../05-reproducible-training/index.md) turns the split and the model fit into stages that DVC can cache and rerun.

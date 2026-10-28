# 09 · Model artifacts, registries, promotion, and lifecycle management

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 14 hours | [06](../06-experiment-tracking/index.md), [08](../08-pipeline-automation/index.md) | Essential |

"Which model is live?" is the question every incident starts with, and the one most teams answer by asking whoever has been there longest. A file called `model_final_v2.pkl` in someone's home directory is not an answer.

A registry makes the answer structural. Versions are immutable, an alias points at exactly one of them, promotion is a decision with gates rather than a rename, and a rollback is one recorded action instead of an archaeology project.

## What you will be able to do

- Package a model so it loads without the training code, and say what that package must contain.
- Register versions and distinguish a version from an alias.
- Write promotion gates that are automatic and measurable, including slice and provenance gates.
- Block a candidate that looks better in aggregate but is worse for a group of users.
- Perform a rollback and state how long it took and what it did not fix.
- Trace a deployed model back to a dataset hash and a commit.

## Start here

1. Read [Concepts](concepts.md) sections 1–6 for artifacts, versions, aliases, and gates.
2. Read the [worked example](worked-example.md): six candidates, two blocked, one promoted, one rolled back — with real registry output.
3. Do the [lab](lab.md): build the registry workflow, then defend it against a model that passes every numeric gate and should still not ship.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the promotion-policy review criteria |
| [Concepts](concepts.md) | Artifacts, signatures, versions, aliases, gates, lineage, rollback |
| [Worked example](worked-example.md) | Six versions and the decisions that separated them |
| [Guided lab](lab.md) | A local registry, a blocked candidate, and a timed rollback |
| [Independent challenge](independent-challenge.md) | A policy that survives a persuasive colleague |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Alias mistakes, unpickling failures, missing lineage |
| [References](references.md) | MLflow registry documentation and model-packaging guidance |

## What you produce

- A candidate model logged with a signature, an input example, metrics, and a dataset hash.
- At least three registered versions and one alias history.
- `promotion_policy.yaml` with gates a machine can evaluate, and a blocked-promotion log.
- A rollback rehearsal with elapsed time and the command used.
- A lineage trace: alias → version → run → dataset hash → commit.

## The reference run

The registry is MLflow's local file store, so nothing here needs a server. Six versions were registered on the course dataset. The champion moved v1 → v2, a later version v5 was promoted, and a rollback returned the alias to v2 in about 2.1 seconds end to end (25 ms for the alias write itself). Those numbers are from this machine; the behaviour is what to remember.

## Next

[Module 10](../10-model-serving/index.md) serves the `champion` alias. It is the first consumer that cares whether the artifact really loads without the training code.

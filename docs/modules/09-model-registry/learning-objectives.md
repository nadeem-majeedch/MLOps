# Learning objectives · Module 09

| # | Objective | Evidence |
|---|---|---|
| 1 | Package a model that loads without training code | A saved artifact with preprocessing, signature, and input example |
| 2 | Version immutably and alias deliberately | A version table and alias history |
| 3 | Gate promotion automatically | `promotion_policy.yaml` plus a command that returns pass or fail |
| 4 | Block a candidate on a slice, not just an aggregate | A recorded rejection that names the zone and the values |
| 5 | Require provenance, not just performance | A gate that fails when training data excludes a production segment |
| 6 | Roll back and measure it | A rehearsal log with elapsed time and the exact command |
| 7 | Trace lineage in both directions | Alias → version → run → data hash → commit, and back |
| 8 | Distinguish local from production registries | A written list of what the local store does not provide |

## Promotion-policy review criteria

A policy is reviewable when a colleague can apply it without asking you:

- [ ] Every gate is a comparison between two numbers, or the presence of a required tag.
- [ ] Each gate names the failure it prevents, not the metric it likes.
- [ ] Absolute and relative gates are distinguished: a ceiling that never moves, a regression limit against the current champion.
- [ ] Slice gates state the population and the tolerance; sparse slices are handled explicitly.
- [ ] Provenance is checked (dataset hash, required segments, commit), not assumed.
- [ ] The failure message names the values, the limit, and the champion it compared against.
- [ ] There is a documented break-glass path that records who, why, and when — not a silent `--force`.

## Thresholds are claims

A tolerance is a statement about acceptable risk, and it should be defended in a sentence. "3% overall" says a small average regression is tolerable if the product accepts it. "5% in Z07" says the sparse-zone error may wobble because 16 test rows cannot support a tighter bound. A gate with no stated reason will be loosened by the first person it inconveniences.

## Self-check before you start

You should be able to run an MLflow experiment locally (Module 06) and explain what a run ID identifies. You do not need prior registry experience.

After the module, you can answer:

1. What is the difference between a model version and an alias, and why does it matter during an incident?
2. Why can a model with the best aggregate MAE still be the wrong model to ship?
3. What does a rollback fix, and what does it leave broken?
4. Why is "the alias points at v2" not enough to reproduce v2 in six months?
5. Which registry features require a server, and what do you lose by staying local?

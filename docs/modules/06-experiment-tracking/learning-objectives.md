# Learning objectives · Module 06

| # | Objective | Evidence |
|---|---|---|
| 1 | Record every run with its inputs | Six runs, each with parameters, dataset hash tag, and model artefact |
| 2 | Compare runs on evidence | A table sorted by MAE, plus the slice columns that change the decision |
| 3 | Design a slice-aware evaluation | Per-zone and peak/off-peak MAE, with row counts shown |
| 4 | Choose a metric and defend it | A paragraph on MAE versus RMSE for this product, including what riders feel |
| 5 | Detect evaluation overfitting | Evidence that the winner was selected on the same rows repeatedly, and a held-out check |
| 6 | Record a baseline | `baseline.json` from an accepted run, with the reason it was accepted |

## The evaluation evidence list

A model-selection decision is reviewable when it includes:

- [ ] The metric that matters to the product, named, with its units.
- [ ] The baseline it is compared against.
- [ ] Aggregate and slice metrics, with slice sizes.
- [ ] The dataset identity (hash or version) for every run.
- [ ] The selection rule, stated before looking at the results.
- [ ] The known weaknesses, including the slice with the worst error.
- [ ] The cost of being wrong in each direction (too high an estimate versus too low).

## Self-check before you start

You should be able to compute and interpret MAE, RMSE, and R², and explain why they differ. If not, read the scikit-learn metrics guide's regression section first.

After the module, you can answer:

1. What is the difference between a parameter, a metric, and a tag?
2. Why is a spreadsheet of results inadequate, specifically?
3. Why can a better MAE be the wrong model to ship?
4. What does a p95 error tell a product manager that MAE does not?
5. How do you know you have overfitted the evaluation set?

# Knowledge check · Module 06

## Questions

1. Distinguish parameter, metric, tag, and artefact, with one example each.
2. Give two specific failures of a spreadsheet as an experiment log.
3. Why is the dataset hash a tag rather than a parameter?
4. What does a local MLflow file store give up compared with a server, and what does it still provide?
5. On this dataset, overall MAE is 2.777 and p95 error is 8.977. Explain both to a product manager in one sentence each.
6. Why report the row count beside every slice metric?
7. Describe one way to overfit the evaluation set and one defence.
8. A candidate improves MAE by 0.1 minutes, but three seeds produce MAE values spanning 0.4 minutes. What do you conclude?
9. Why record a baseline as a run in the same experiment rather than a number in a document?
10. What does MLflow not tell you about an experiment?

## Answers and reasoning

**1.** Parameter: a value you choose (`max_depth=12`). Metric: a measured outcome (`mae=2.777`). Tag: context that is not a choice (`data_hash=847fa5b8`). Artefact: a produced file (`model/`). *Reasoning:* parameters are for comparison across runs; tags describe conditions.

**2.** (a) Nothing links a row to the code and data that produced it, so a surprising result cannot be reproduced. (b) It does not enforce structure, so two people edit it and the "best" row becomes ambiguous. A third: it cannot store the artefact.

**3.** You do not optimise a dataset hash to improve a metric; it describes the conditions under which the run happened. Treating it as a parameter would imply runs with different hashes are comparable alternatives, which they are not.

**4.** It gives up shared access, the model registry, and concurrency. It still provides run records, artifact storage, parameter/metric search, and an API that transfers to a server unchanged.

**5.** "On average, the estimate is wrong by about 2.8 minutes." "One trip in twenty is wrong by more than 9 minutes." The second is the number to quote when discussing riders who miss appointments.

**6.** Because a metric computed on 17 rows has wide uncertainty and can reverse with one more week of data. Reporting the count prevents a small slice from being treated as a stable fact.

**7.** Compare dozens of variants on the same test rows and pick the best; the winner's score is optimistic. Defence: fix the selection rule before looking, hold out a final untouched set, and report how many comparisons were made.

**8.** The improvement is not distinguishable from run-to-run variation; do not claim it. Either collect more test data, reduce variance, or choose on a different criterion - but do not ship on a difference smaller than the noise.

**9.** Because a run carries its code, data hash, and environment, so the comparison is checkable, and because a baseline in a document drifts out of date without anyone noticing. The same experiment also makes the gap visible in every comparison view.

**10.** Whether the experiment was well designed, whether the slices are the right ones, whether the metric matches the product's cost structure, and whether the model should exist. It records; it does not judge.

## Scoring

| Score | Next step |
|---|---|
| 8–10 | Continue to Module 07 |
| 5–7 | Reread sections 3–6 of [Concepts](concepts.md), then redo the lab's Part 4 |
| 0–4 | Re-run the six experiments and read the comparison table before continuing |

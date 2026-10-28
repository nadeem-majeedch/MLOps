# Knowledge check · Module 04

## Questions

1. What are the three ways a data contract can fail, and which check type catches each?
2. Why is a validation message naming an example row more useful than a count alone?
3. A pipeline silently drops rows with negative distances. Give two concrete harms.
4. What is the difference between an outlier and an error? Give one example of each from this dataset.
5. Explain why `fare_amount` produces a misleading MAE of 0.66 minutes.
6. Why does a random split over time-ordered data overstate model quality?
7. What does a `.dvc` file contain, and what does it deliberately not contain?
8. Where does the data itself go after `dvc add`, and what must exist for another machine to retrieve it?
9. Name two things DVC does not provide that a production pipeline needs.
10. A dataset passes all eight checks. Name two ways it can still be unfit for training.

## Answers and reasoning

**1.** Shape (column presence/type), values (ranges and cross-field plausibility), and meaning (a valid code that now refers to something else). The first two are automatable; the third needs an owner for the vocabulary.

**2.** Because validation is a diagnostic task. A count tells you the scale; an example gives you a row to open, a query to run, and a person to call. Naming the first offending row deterministically also lets two people discuss the same record.

**3.** (a) The training population silently changes, so metrics move without any recorded decision; (b) the producing team never learns their feed is broken, so the defect recurs. A third: the discarded rows may be exactly the segment the model is worst at.

**4.** An outlier is a legal but unusual value: a 55 km airport trip. An error is an impossible value: a −3.68 km distance, or 40 km in 5 minutes. Range checks should encode physical limits; percentiles would fail every holiday.

**5.** Because the fare is computed by the meter partly from the trip's duration. The model is not predicting duration; it is recovering a number that was a function of the answer. At booking time the fare does not exist, so the model cannot be served at all.

**6.** Because future rows (and rows from the same days) appear in both train and test, so the test set shares the conditions the model was fitted on. It measures interpolation within a known period, not extrapolation to the next week, which is what deployment requires.

**7.** It contains the content hash (md5), size, and path of the tracked file. It does not contain the data, any credential, or the history of how the file was produced.

**8.** Into `.dvc/cache`, stored under a path derived from the hash. For another machine to retrieve it, a configured **remote** must hold the objects, and the colleague runs `dvc pull` with the same `.dvc` file. Without a push, the remote has nothing.

**9.** Any two of: pipeline stage graph and cache invalidation (Module 05), run and experiment records (06), schema validation (this module's checks are separate), access control and encryption at rest (15).

**10.** Any two: it can be unrepresentative of the serving population; it can contain a leaky column; it can be stale relative to the world; it can have the right shape but the wrong join (a zone vocabulary that is valid but mis-assigned); or labels can be systematically wrong.

## Scoring

| Score | Next step |
|---|---|
| 8–10 | Continue to Module 05 |
| 5–7 | Redo Part 5 of the lab, and reread section 4 of [Concepts](concepts.md) |
| 0–4 | Rebuild the validation report from the worked example, then repeat the lab's Parts 2–3 |

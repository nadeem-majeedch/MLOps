# Knowledge check · Module 09

## Questions

**1.** A colleague proposes renaming `model.joblib` to `model_v7_final.joblib` instead of registering a version. Name two problems that appear within a month.

**2.** Why does the reference artifact save the whole scikit-learn `Pipeline` rather than the fitted `RandomForestRegressor`?

**3.** Serving code uses `models:/raviride-eta@champion`. An evaluation script also uses `@champion`. What is wrong with the evaluation script?

**4.** A candidate improves overall MAE by 1% and worsens Z07 by 6.4%. The Z07 test slice has 16 rows. Give the argument for refusing it and the argument for accepting it.

**5.** Version 5 trained on 849 rows; every other version trained on 896. No gate failed. What kind of gate was missing, and what would its failure message say?

**6.** Rollback took 2.1 seconds. Why is that number small, and name two things the rollback did not fix.

**7.** The champion's tags include `data_hash=285bbf8406f483a9` and `git_commit=ac4246f`. Which incident questions can you answer with each, and which can you not answer with either?

**8.** Why are stages deprecated in favour of aliases? Give one concrete workflow that aliases support and stages cannot.

**9.** Your policy has a `--force` flag used twice last quarter, both times successfully. What should you do?

**10.** You keep the registry on a local file store. Name three capabilities you do not have, and one way the absence of each could hurt you.

---

## Answers and reasoning

**1.** First, the old name is overwritten or duplicated, so "which file is live?" becomes a naming convention that nobody enforces — and the file's contents cannot be tied to the data that produced it. Second, two people will produce `model_v7_final` for different experiments, or `model_v7_final_FIXED`, and the newest modification time will be treated as the truth. Neither problem is about storage; both are about the absence of an immutable identifier and its metadata.

**2.** Because preprocessing is part of the model's behaviour. The forest expects nine numeric columns plus three categorical ones in a specific order, with the same encoding. Saving the pipeline makes the artifact self-contained: it can transform raw feature rows itself. Saving the forest alone would force the serving code to reimplement the `ColumnTransformer`, which is the train/serve skew this course keeps returning to.

**3.** An evaluation that follows `@champion` measures a moving target: the same script produces different numbers as promotions happen, and a comparison across weeks mixes model changes with code changes. Evaluations should pin a version (`models:/raviride-eta/7`); only serving should follow the alias.

**4.** Refuse: 16 rows is small but not meaningless, the direction is consistent with the aggregate improvement coming from other zones, and Z07 users are a real population whose experience would degrade. Accept: with 16 rows the 95% confidence interval on MAE is wide enough that 6.4% may be noise, the aggregate gain is real, and the policy's job is to serve the majority well. The defensible position is to state which argument the team accepts and set the tolerance accordingly — not to promote silently and describe it as an improvement.

**5.** A provenance gate: the candidate's training data excluded a production segment. The message should name the segment and the row deficit, for example `training data excludes production zones: Z08 (849 rows vs 896 for the champion)`. Performance gates cannot see this because the test set still contains Z08, and 22 rows produce a change inside the tolerance.

**6.** Small because the artifact already exists: rollback changes one pointer, not a model. It did not fix the cause (the missing gate), and it did not undo downstream effects — predictions already served, caches written, dashboards refreshed. It also does not reload a running server that cached the old model in memory.

**7.** `data_hash` answers "which exact feature files trained this model", assuming the hash is of the data and the mapping to a stored dataset version exists. `git_commit` answers "which code produced it". Neither answers "was the training data correct for the product", "did the evaluation use the same split", or "is the model still accurate today". Those need policy, tags about segment coverage, and monitoring.

**8.** Stages assume one linear lifecycle: a version is in exactly one stage, and the transitions are fixed. Aliases are labels, so a version can be `champion` in one region and `challenger` in another, or simultaneously `last-known-good` and `eu-west`. A canary or regional rollout cannot be expressed with single-valued stages without inventing parallel registered models.

**9.** Treat each use as an incident. Read the recorded reason, check whether the policy was wrong (then change it deliberately) or the process was bypassed (then fix the process). Two successful overrides in a quarter means the policy does not match reality; a policy that is routinely overridden trains people to ignore it. If the override is legitimate and repeatable, encode it as a gate or an allowance.

**10.** No authentication or authorisation: anyone with filesystem access can move `champion`, and you cannot prove who did. No concurrent-writer safety: two people running the workflow against the same directory can interleave writes. No durable artifact store or audit log: losing the laptop loses the registry, and there is no independent record of promotions. A local store is fine for learning and for one developer; it is not evidence in an incident review.

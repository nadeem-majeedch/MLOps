# Knowledge check · Module 17

## Questions

**1.** A clean clone produces MAE 2.91 against your reported 2.77. What are the first three things you check, and when is the difference acceptable?

**2.** Your gate passes a model that swapped kilometres for miles. Is that a test problem or a gate problem, and what would you add?

**3.** You have evidence of a green CI run but no failing run. Why is that insufficient for the capstone?

**4.** An alert fires on drift, but accuracy is unchanged. What do you do, and what do you not do?

**5.** Rollback took 40 minutes because the previous image tag had been overwritten. What would you change, and what does that imply about tags?

**6.** A peer deploys from your runbook in 55 minutes and asks three questions. What are the three questions likely to be, and what do you do with them?

**7.** During the incident simulation, you have a hypothesis but no confirming evidence after 10 minutes. What do you do next?

**8.** Your model card says "the model may be biased". Why is that insufficient, and what would you write instead?

**9.** The defence asks "what breaks at ten times the load?" You have not load-tested. What is an honest answer?

**10.** You have 10 hours left and three unfinished artefacts: the runbook, the model card, and a canary deployment. What do you cut, and why?

---

## Answers and reasoning

**1.** Check the data version/hash, the dependency versions (especially scikit-learn and NumPy), and the seed/split. Then check whether the README's commands were followed exactly. A difference is acceptable if it is within the tolerance you stated **before** the run and you can explain the cause (sampling, library version, platform). A 5% difference with no explanation is not acceptable; it means the reproduction claim is not yet established.

**2.** Both, usually. The test did not exercise the unit boundary, and the gate did not include a contract or equivalence check. Add a test with a known distance and a known expected prediction, and a single-record equivalence test between the training and serving feature paths. The gate should fail when the unit changes, not only when the aggregate metric moves.

**3.** A green run proves the happy path works; it does not prove the gate can stop a bad release. The capstone requires evidence that the gate fails for the right reason on schema, unit, and metric regressions. Without a failing run, a gate is indistinguishable from a step that always succeeds.

**4.** Investigate the change in population; check whether it is persistent, whether a slice got worse, and whether a deploy or data change explains it. Do not retrain reflexively. Drift can accompany better accuracy (Module 14's zone-shift batch), and retraining on a drift signal alone can replace a working model.

**5.** Change the release process to pin images by digest, keep previous versions pullable, and record the digest in the deployment record. Tags are mutable labels; a rollback to a tag is only a rollback if the tag still points at the old image. The implication: treat the digest as the identity, the tag as a convenience.

**6.** Likely questions: which directory to run from, which credentials/environment variables are needed, and how to tell whether it worked. Each question is a missing line in the runbook. Add the answer, then have the next peer try again; do not simply answer the questions verbally.

**7.** Stabilise first if users are affected. Then state the hypothesis, the evidence that would confirm it, and a timebox. If the evidence is not available, test the next most likely cause or restore to the last known good version. Do not keep investigating without a hypothesis; write down what you ruled out.

**8.** It is a label, not a limitation. Write the group, the metric, the row count, the threshold, and the consequence: for example, "FPR is 0.033 in fall and 0.143 in spring on 45/55 test rows; a spring rollout should review the threshold before enabling automatic flags." A reader can act on that; "may be biased" gives them nothing.

**9.** Say you have not measured it, name the first bottleneck you expect and why, and describe the test you would run: the load profile, the metric, and the pass/fail threshold. An honest unknown with a measurement plan is better than an invented number. The defence is testing judgement, not omniscience.

**10.** Keep the runbook and the model card; cut the canary. The runbook and card are required artefacts and are cheap to finish; the canary is an extension that needs a cluster, a load profile, and time to observe. Cutting the canary is a scope decision; shipping a broken runbook is a handover failure. State the cut and the reason in the decision record.

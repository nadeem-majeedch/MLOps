# Knowledge check · Module 01

Answer in writing before reading the answers. Ten questions, about 25 minutes. Marking yourself honestly matters more than the score: each answer's reasoning tells you which section to reread.

## Questions

1. Give the shortest definition of MLOps that is still accurate, and name one thing that definition excludes.
2. A model's precision falls from 0.81 to 0.68 over two months. The code has not changed. Name three different causes and the lifecycle stage each belongs to.
3. What artefact does the evaluation stage produce, and why is a single aggregate metric an inadequate artefact?
4. Explain the difference between deploying and releasing a model, and give one consequence for who approves what.
5. A team validates features identically in training and serving. Name one remaining source of training/serving skew.
6. Why does "retrain on the latest data" need a caveat in a system that acts on its own predictions?
7. Name three categories of hidden technical debt and, for each, one symptom a new reviewer would notice.
8. Your team's maturity is "level 2". Name one thing that is still not guaranteed, and why the level number can mislead.
9. Which stage owns a defect that was introduced by an upstream schema change and noticed by users? Justify your answer in one sentence.
10. A postmortem concludes "root cause: engineer error". Give two specific ways to rewrite it so that it produces useful actions.

## Answers and reasoning

**1.** *MLOps is the practice of keeping a machine-learning system correct while it changes and after its inputs change.* It excludes model research: improving a model's accuracy on a fixed benchmark is machine learning work, not operations. A definition that includes research stops being checkable, because there is no "done".

**2.** Any three of: an upstream feed changed its units or schema (data stage); the population shifted, for example a new city (framing or data, depending on whether the model's scope was declared); a dependency upgrade altered preprocessing (deployment or environment); the model is being compared against a different label definition (evaluation); or a feedback loop narrowed the data the model sees (monitoring and data). *Reasoning:* "no code changed" is never an explanation in itself. Behaviour is a function of code, data, and world.

**3.** Metrics plus a slice table plus an evaluation report: what was measured, on which rows, against which baseline. A single aggregate hides the segment where the model got worse. Module 06's lab shows a real case where an overall improvement coexists with a worse zone.

**4.** Deployment puts an artefact behind an endpoint and is reversible and mostly invisible. Release exposes it to real decisions and requires evidence and a named approver. Consequence: an engineer may be allowed to deploy automatically but not to release; the release decision belongs to whoever owns the business risk.

**5.** Any of: different data availability (the request lacks warehouse-only fields); different missing-value defaults; different library version in the two paths; different time zone or currency handling; feature computed from a join that is only possible offline. Identical feature *code* does not guarantee identical feature *values*.

**6.** Because the training data was produced partly by the previous model's decisions. Retraining on it can reinforce existing coverage gaps: the system sees outcomes only for the cases it already acted on. The caveat is that you need data about the counterfactual, or an explicit exploration policy, before "latest data" means "better model".

**7.** Glue code (a large block of conditionals around a library call); pipeline jungles (scripts calling scripts with manual steps, so no clean rerun exists); configuration debt (paths and thresholds scattered and hard-coded, so a value change needs a deploy); undeclared consumers (another team queries your output table directly); data dependencies (an upstream feed whose schema nobody owns). *Reasoning:* these are visible in structure, not in tests, which is why they are called hidden.

**8.** At level 2, pipeline changes deploy automatically, but nothing guarantees the *monitoring response* is defined, or that the model's scope is still appropriate. The level describes automation of the pipeline, not the quality of the judgement around it, and a poorly understood level-2 system is worse than a careful level-1 one.

**9.** The data stage, because that is the earliest point at which a check could have compared the incoming schema with the expected one. Users are where it became visible, not where it was made. If the schema change was legitimate, then framing owns the decision about whether the model may still consume it; either answer is defensible if argued, but "monitoring" is not, because monitoring only detects.

**10.** Replace the person with the conditions: (a) "the deploy script overwrote the production configuration because there was no distinction between environments", and (b) "the manual checklist was skipped because nothing enforced it". Then add the controls that make the condition impossible or visible: separate configuration per environment; a pipeline that fails when a required check has not run. *Reasoning:* an action you can assign, test, and close must name a system condition, not a state of mind.

## Scoring yourself

| Score | What it means |
|---|---|
| 8–10 | Move to Module 02 now |
| 5–7 | Reread sections 2, 5, and 6 of [Concepts](concepts.md), then continue; the later modules assume 2 and 6 |
| 0–4 | Do the [guided lab](lab.md) before continuing. The lab is where the vocabulary becomes usable |

# Learning objectives · Module 01

Each objective states what you must be able to *do*, not what you must have read. The third column is the evidence a reviewer would accept.

| # | Objective | Evidence that you can do it |
|---|---|---|
| 1 | Define MLOps and distinguish it from ML engineering, data engineering, and DevOps | A four-row comparison table you wrote yourself, with one example task per row |
| 2 | Describe the ML lifecycle and name the artefact each stage produces | A lifecycle diagram where every arrow is labelled with what it passes on |
| 3 | Place a failure at the correct lifecycle stage | Classification of eight events from the lab timeline, each with a justification sentence |
| 4 | Name the control that would have caught a given failure | A postmortem section mapping each contributing factor to a control and to the module that teaches it |
| 5 | Explain hidden technical debt with three concrete examples | Three examples from systems you have used, each naming the debt category and its cost |
| 6 | Distinguish deployment from release | A short paragraph explaining who can trigger each, and what each one exposes to riders |

## Before you start: a one-minute self-check

Answer these in your head. If most are already clear, you can move faster through [Concepts](concepts.md) and spend your time on the lab.

1. What is the difference between training a model and serving it?
2. What artefact does training produce, and what does serving consume?
3. If a model's predictions get worse but its code did not change, what changed?
4. Who decides that a model is allowed to face customers?

If question 3 or 4 is unclear, that is the normal starting point; both are the subject of this module.

## After you finish: the same self-check

You are done when you can answer all six of these without notes:

1. Where does data engineering stop and MLOps start?
2. Which lifecycle stage owns the training/serving skew defect, and why?
3. Why is "the model is deployed" not the same claim as "the model is released"?
4. What are the five categories of hidden technical debt, and which one is hardest to see in a code review?
5. What does a maturity level describe, and what does it not describe?
6. Which of the eight lab events would a monitoring dashboard have caught, and which would it have missed?

If any answer is shaky, reread the matching section of [Concepts](concepts.md) rather than moving on. Module 03 reuses the debt vocabulary directly.

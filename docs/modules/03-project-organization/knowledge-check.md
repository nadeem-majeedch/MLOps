# Knowledge check · Module 03

## Questions

1. Name the four kinds of project content that change for different reasons, and one rule for each.
2. A path is hard-coded and correct today. Give two distinct reasons it is still debt.
3. What is the difference between a setting and a secret, and where should each live?
4. Why does `config` import nothing from the rest of the project?
5. Your refactor produced a different MAE. List three likely causes in the order you would check them.
6. What must an ADR contain that a commit message cannot?
7. Which technical-debt category is hardest to see in code review, and why?
8. Why is "delete the notebook and the pipeline still trains" a good test of extraction?
9. What does a circular import tell you about module boundaries?
10. A debt item has no cost estimate. What happens to it in a planning meeting, and what should you do instead?

## Answers and reasoning

**1.** Code (behaviour), configuration (environment or experiment choices), data (the world), outputs (one run's artefacts). Rules: code contains no literals a human might change; configuration contains no logic; data is versioned, not committed as a file to Git; outputs are regenerated, never hand-edited.

**2.** Correctness today is not durability: (a) the path encodes one machine's layout, so it fails for the next person or in a scheduled job; (b) it hides a decision that belongs in configuration, so changing environments requires editing and reviewing code. A third, if you want it: it makes the module untestable outside that directory.

**3.** A setting may be read by anyone who can read the repository and is safe to review; a secret grants access and must be readable by as few people as possible. Settings go in `params.yaml`; secrets come from environment variables or a secret manager, never committed, never logged.

**4.** To keep the dependency graph acyclic and the module testable. `config` is the bottom of the graph: paths and parameters that everything else may use. If `config` imported `train`, any import would drag in scikit-learn, and a test of parameter loading would build a model.

**5.** Row order before splitting; the split boundary (`<` versus `<=`) or the date cutoff; seed or hyperparameters; a feature list that gained or lost a column. Check row counts first because they discriminate between those causes in one step.

**6.** The alternatives that were rejected and the consequences accepted. A commit says what changed; an ADR says why this option and not the others, and what you agreed to live with.

**7.** Undeclared consumers. Nothing in *your* repository references the external reader, so no review, test, or import graph shows the dependency; you discover it when you change a schema.

**8.** Because a notebook can succeed while containing logic that only works in its own execution order. If the pipeline trains without the notebook, the logic lives in modules and the notebook is a view, not a source.

**9.** That two responsibilities are coupled in both directions - often because a shared helper sits too high, or because what should be one module was split by file type rather than by role. The fix is structural, not an import trick.

**10.** It is deferred indefinitely, because it cannot be compared with work that has a price. Estimate roughly (S/M/L with hours), assign an owner role, and state the risk in consequences; then it can compete.

## Scoring

| Score | Next step |
|---|---|
| 8–10 | Continue to Module 04 |
| 5–7 | Reread sections 1–3 and 5 of [Concepts](concepts.md), then redo Part 4 of the lab |
| 0–4 | Rebuild the refactor from the worked example by hand before attempting a project of your own |

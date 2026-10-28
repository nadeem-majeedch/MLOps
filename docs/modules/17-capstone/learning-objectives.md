# Learning objectives · Module 17

| # | Objective | Evidence |
|---|---|---|
| 1 | Define a system boundary and an out-of-scope list | A one-page scope with users, decisions, and excluded uses |
| 2 | Reproduce the system from a clean clone | A timed clean-clone run and the reported metric |
| 3 | Prove data and model lineage | Alias → version → run → data hash → commit, with no unexplained `unknown` |
| 4 | Make a gate that fails for the right reason | Three injected regressions with the failing output retained |
| 5 | Serve a validated contract | Five malformed requests with specific 422 messages |
| 6 | Operate the service | A runbook a peer uses to deploy in under 30 minutes |
| 7 | Monitor and decide | A drift report, an alert, and a retraining or rollback decision |
| 8 | Recover under pressure | A timed rollback and a verified restoration signal |
| 9 | Diagnose an injected incident | A timeline, hypothesis, evidence, and postmortem |
| 10 | Defend the design | Answers to "why not simpler?" and "what breaks at 10× load?" |

## Capstone readiness gate

Do not start the build until these are true. They are the minimum, not the whole rubric.

- [ ] Modules 04, 07, and 14 are complete: you have validation, tests, and a monitor you wrote.
- [ ] You can run the pipeline from a clean environment without editing code.
- [ ] You have a model artifact with a signature and a recorded data hash.
- [ ] You have served the model and sent a malformed request that returned 422.
- [ ] You have a repository you can clone, with a README that a peer can follow.
- [ ] You have 35–48 hours in your calendar, spread over at least four weeks.
- [ ] You have a place to record evidence that is not your memory.

If you cannot check the first three, do the relevant module lab before starting. A capstone built on an unreproducible pipeline produces an unreproducible capstone.

## What "done" means

The capstone is not done when the code runs. It is done when:

1. **A stranger can run it.** They have the README and the repository, not your terminal history.
2. **A gate can stop it.** You have shown a failing run, not only a green one.
3. **A failure can be diagnosed.** You have a timeline and an evidence path, not a story.
4. **A limitation is written down.** The model card names who is affected and what the system must not do.
5. **A decision can be defended.** You can explain why the system is this size and what would break at scale.

## Self-check before you start

Answer these in one sentence each:

1. Who uses the prediction, and what decision does it change?
2. What data enters, and what data must never enter?
3. Which failure would be most harmful, and which control catches it first?
4. What is the smallest version that is still useful?
5. What will you deliberately not build?

If you cannot answer 1 and 4, the scope is too large. If you cannot answer 3, the monitoring plan is decoration.

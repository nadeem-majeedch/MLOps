# Concepts · Integrating a lifecycle, then handing it over

## 1. The capstone is an integration problem, not a new-tool problem

You already have the pieces: validation, a pipeline, tracking, a registry, an API, a container, CI, a scheduler, a monitor. The capstone is the evidence that they work **together**, from a clean copy, without you.

That changes what "done" means. In Module 05, a pipeline was done when it reproduced a metric on your machine. In the capstone, it is done when a stranger reproduces it from the README, with the same data version, in a time you can state.

The most common capstone failure is scope: a new database, a new orchestrator, a new cloud service, and no handover. The second is a demo that works only in the author's terminal. Both are avoidable by writing the boundary first.

## 2. Write the boundary before the architecture

A system boundary is a short statement of:

- **the decision** the prediction changes (assign a driver, offer support, schedule maintenance);
- **the user** and what they see;
- **the input** and its provenance;
- **the output** and its uncertainty;
- **what is out of scope** (credit decisions, medical advice, disciplinary action);
- **the failure mode** that matters most.

The out-of-scope list is not a disclaimer; it is a design constraint. If the system must not be used for disciplinary action, then the output should not look like a verdict, the UI should not rank people, and the model card should say so. A limitation that exists only in the README is not a control.

A useful test: draw the system on one page. If you cannot, the boundary is unclear, and the documentation will be unclear too.

## 3. Clean-clone reproducibility

The clean-clone test is the capstone's central exam. It answers: can someone who is not you rebuild the environment, the data, the model, and the metric?

A reproducible capstone has:

- a **README** with prerequisites, install, data generation, training, test, and run commands, in order;
- **pinned dependencies** (direct and transitive) and a recorded Python version;
- a **data version** with a hash or a manifest, and a generator if the data is synthetic;
- **seeds** for every stochastic step, and a statement of what remains non-deterministic;
- a **metric** with a tolerance, not a single cherry-picked number;
- **no hidden state**: no notebook output, no local file that is not generated, no environment variable that only you have.

The honest version of reproducibility is a tolerance: "MAE 2.77 ± 0.05 on this machine with these versions". A claim of exact equality across operating systems and BLAS builds is usually false. State the tolerance and what causes variation.

Test it by cloning to a new directory, creating a fresh environment, and following only the README. Time it. Every undocumented step is a defect.

## 4. Gates that fail for the right reason

A gate is only evidence if it can fail. The capstone requires three injected regressions:

| Regression | What it proves | Example |
|---|---|---|
| Schema | Validation catches a broken contract | Rename `distance_km` to `distance`, or change a unit |
| Unit/model | Tests catch a wrong computation | Swap kilometres for miles in the feature builder |
| Metric | The quality gate catches a real degradation | Train a shallow model, or corrupt a slice |

For each, keep the failing output and the exit code. A gate that fails because the test file is missing, or because the environment is broken, proves nothing about the gate. The failure must name the artefact and the reason.

A good gate has:

- a **threshold** derived from evidence, with the evidence recorded;
- a **scope**: overall, per slice, and provenance;
- a **failure message** that says what to do next;
- **no escape hatch** that is used routinely. A `--force` flag is acceptable if every use is recorded; an override that everyone uses is a rubber stamp.

## 5. Observability: the three questions

Monitoring is not a dashboard; it is the ability to answer three questions:

1. **Is the service working now?** Availability, latency, error rate, saturation.
2. **Is the model still appropriate?** Input drift, prediction distribution, performance on labelled data, slice metrics.
3. **What changed?** Deployments, alias moves, data batches, configuration, dependency updates.

The third question is the one capstones usually miss. An alert without a timeline of changes becomes a guessing game. Record deployments and promotions in the same place as the metrics, or at least with a timestamp you can join.

An alert is actionable when it names:

- what fired and against which threshold;
- which service, model version, and environment;
- the first diagnostic step;
- the owner and the escalation path;
- what "resolved" looks like.

## 6. Incident command for one person

A solo capstone still needs an incident process. The minimum:

1. **Declare.** Write down the start time and the symptom. Do not start changing things before you have a timeline.
2. **Stabilise.** Roll back or disable the feature before diagnosing, if users are affected. Restoration first, root cause second.
3. **Hypothesise.** State the most likely cause and the evidence that would confirm or reject it. Write it down before you look.
4. **Gather evidence.** Logs, metrics, deploy records, model version, a single-record comparison. Timebox each check.
5. **Restore.** Apply the fix, verify with a signal, record the time.
6. **Review.** Timeline, impact, root cause, contributing conditions, prevention items with owners.

The capstone's incident simulation is timed for a reason: with unlimited time, everything is diagnosable. The skill is to form a hypothesis, test it, and restore service without thrashing.

## 7. Handover: the runbook is the product

A handover package is not a repository dump. It is the minimum set of documents a competent peer needs:

| Document | Question it answers |
|---|---|
| README | What is this, how do I run it, what does it not do? |
| Architecture | What are the components, and why these? |
| Runbook | How do I deploy, roll back, and handle the top three alerts? |
| Model card | What is the model for, how well does it work, who might it harm? |
| Postmortem | What happened, and what changed? |
| Evidence | How do I know the gates and the rollback work? |

Test the runbook with a peer who has not seen the project. Give them the repository and a time limit; do not answer questions during the attempt. Every question they ask is a missing line.

## 8. The defence: why not simpler?

The defence is not a tour of the code. It is a test of judgement. Prepare answers to:

- **Why not simpler?** Name the failure the complexity prevents, and its cost. If you cannot, the complexity is not justified.
- **What breaks at 10× load?** Name the first bottleneck: the model server's concurrency, the database, the feature computation, the registry, the log volume. Give a number or a measurement plan.
- **Which decision would you change?** Name one, and the evidence that changed your mind.
- **What is the top residual risk?** Name it, its owner, and the signal that would reveal it.
- **What does the system not do?** The out-of-scope list, without hedging.

A good defence is short and specific. "We used Kubernetes because it is industry standard" is not an answer; "we used Compose because a single node meets the latency target and the team is one person" is.

## 9. Scope discipline under time pressure

The capstone is 35–48 hours. A realistic allocation:

| Phase | Core | Full |
|---|---|---|
| Scope and boundary | 3 h | 3 h |
| Pipeline, data version, clean clone | 8 h | 8 h |
| Tests and CI gate | 7 h | 8 h |
| Serving and container | 6 h | 7 h |
| Monitoring and alert | 5 h | 6 h |
| Runbook and model card | 4 h | 5 h |
| Incident simulation and postmortem | 3 h | 4 h |
| Defence and portfolio | 3 h | 3 h |
| Contingency | 4 h | 4 h |

If a phase overruns, cut scope, not evidence. A Core capstone with a working rollback beats a Full capstone with a broken one.

## 10. What the assessor is looking for

Across the artefacts and the cross-cutting criteria:

- **Reproducibility**: a clean clone, pinned versions, a stated tolerance.
- **Evidence**: failing runs, timed rollback, alert output, a peer's handover time.
- **Judgement**: a boundary, a trade-off, a rejected option.
- **Honesty**: limitations, residual risk, what was not tested.
- **Operability**: a runbook someone else used.

The weakest capstones are impressive demos with no failing evidence. The strongest are modest systems with a clear boundary and a trail that a stranger can follow.

## 11. After the capstone

The capstone is the beginning of a portfolio, not the end of learning. Two habits to keep:

- **Keep the evidence.** A failing CI run and a timed rollback are more persuasive than a list of tools.
- **Write the decision record.** A short note on what you chose, what you rejected, and what would change your mind is the most reusable artefact you will produce.

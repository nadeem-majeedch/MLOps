# Troubleshooting · Module 17

## Diagnose in this order

1. **Scope**: is the thing you are debugging inside the boundary, or has the project grown?
2. **Reproduction**: does it fail from a clean clone, or only in your environment?
3. **Version**: data, code, dependencies, model, container — which one moved?
4. **Gate**: did it fail for the stated reason, or for a harness reason?
5. **Service**: health, readiness, contract, logs.
6. **Model**: input distribution, prediction distribution, labels, slice.
7. **Evidence**: what would prove the fix, and what would prove it failed?

## Failure table

| Symptom | Likely cause | Fix |
|---|---|---|
| Clean clone fails on the first command | Undocumented prerequisite or absolute path | Add it to the README; use repository-relative paths |
| Metric differs beyond tolerance | Data version, library version, seed, or a leaked feature | Record the hash and versions; fix the split; state the tolerance |
| Tests pass locally, fail in CI | Missing fixture, environment variable, or service | Make the test self-contained; add the fixture; use a service container |
| Gate passes a bad model | Threshold too loose, or the test does not exercise the path | Tighten with evidence; add a schema/unit/equivalence test |
| Gate fails on everything | Harness error, missing data, or an unreachable service | Fix the harness before tuning the threshold |
| API 500 on a malformed request | Validation missing or an unhandled error | Add the schema rule; return 422 with a specific message |
| `/ready` passes but predictions fail | Readiness checks the process, not the model | Make readiness load the artifact or verify a prediction |
| Alert fires constantly | Threshold too low, reference stale, batch too small | Add a minimum sample; re-baseline; require two signals |
| Alert never fires | Threshold too high, monitor broken, or no data | Inject a known shift; check the last-success timestamp |
| Rollback is slow | Approval, image pull, or a missing previous version | Pre-approve out-of-hours rollback; pin digests; rehearse |
| Peer cannot deploy | Runbook assumes your terminal | Watch them, record every question, fix the doc |
| Postmortem rejected | Blame, missing timeline, or unverifiable prevention | Rewrite as system conditions; cite timestamps; add checks |

## Case 1: the clean clone that is not clean

The README says `python run_pipeline.py`. On a fresh machine it fails: `dvc: command not found`, then a missing `data/raw/trips.csv`, then a package import error.

This is not bad luck; each is an undocumented dependency. Fix the README in the order a stranger hits them:

1. Python version and virtual environment;
2. install command and the lock file;
3. data generation command;
4. DVC initialisation (and why `--no-scm` is used in this repository);
5. pipeline command;
6. test command;
7. expected metric and tolerance.

Then clone again and follow it literally. If you have to think, the README is incomplete.

## Case 2: the gate that cannot fail

You inject a schema regression, run CI, and it passes. The test suite is green.

Possible causes:

- the test imports the old schema and never exercises the new code path;
- the schema change is in a fixture, not the production path;
- the gate runs unit tests but not the contract test;
- the test is skipped because an environment variable is missing;
- the pipeline catches the exception and returns a default.

Fix the **test**, not the threshold. A gate that cannot fail is worse than no gate because it creates false assurance. Keep the failing run as evidence once it works.

## Case 3: the incident with no timeline

You notice a drop, start debugging, and two hours later cannot say when it began or what changed.

The missing artefact is a change log. During the incident:

1. write the first observed time and the symptom;
2. list recent deploys, alias moves, data batches, and configuration changes with timestamps;
3. state one hypothesis and the evidence that would confirm it;
4. timebox each check;
5. restore, verify, record.

Afterwards, add the change log to the runbook. An alert without a timeline turns every incident into archaeology.

## Case 4: the handover that fails silently

The peer says "it worked" but cannot reproduce the metric, or deployed an older image, or skipped the gate.

Ask for the commands and the output, not the conclusion. A handover is verified by artifacts:

- the clone command and the commit;
- the install command and the resolved versions;
- the pipeline command and the metric;
- the deploy command and the running version;
- the rollback command and the time.

If the peer cannot produce them, the runbook is not finished. Observe the next attempt and write down every question.

## Case 5: the capstone that grew

You are three weeks in and have added a new database, a message queue, and a cloud deployment. The Core artefacts are unfinished.

Stop. Re-read the boundary. For each new component, ask: which required artefact does this improve, and what failure does it prevent? If the answer is "it would be more realistic", cut it or move it to the Full variant.

A smaller system with a working gate, a timed rollback, and a peer handover is a pass. A larger system with none of those is a demo.

## Case 6: the model card that says nothing

The card repeats the README and says "may be biased". A reviewer cannot act on it.

Replace generic statements with measured ones:

- the metric, the split, the threshold, the date;
- the groups with row counts and the disparity;
- the populations not represented;
- the prohibited use and the reason;
- the monitoring signal and the owner.

If a sentence would be true of any model, delete it.

## When to stop and ask for help

Escalate when:

- the capstone requires a paid service you do not have;
- a real credential or personal data has entered the repository;
- the only way to make the gate pass is to weaken it;
- the incident involves data loss or a destructive migration;
- the scope cannot be finished in the time available.

The last one is a scope decision, not a failure. Cut an extension, keep the evidence, and say what you did not do.

# Module practice exercises

Two short exercises per module, for the gap between reading a lesson and doing
its lab. Each takes 20–40 minutes, needs only what the module already introduced,
and produces something you can check.

Use them in one of three ways:

- **Before the lab**, to find out whether the concepts landed.
- **After the lab**, as a variation that is not step-by-step.
- **During revision**, when a full lab is too slow.

The exercises assume the `raviride-eta` project from the course. Where a module
has no code yet (01 and 15–17), the exercise produces a document instead.

---

## Module 01 · MLOps foundations

[Module 01 page](../modules/01-introduction-to-mlops/index.md) · [Lab](../modules/01-introduction-to-mlops/lab.md)

**1.1 Map a failure to its stage.** Choose a public ML failure you can read about
(a search for "machine learning model failure postmortem" will give you several).
Write a five-row table: symptom, immediate cause, lifecycle stage that should
have caught it, artefact that would have provided the evidence, one control.
Then answer: which stage was skipped first?

**1.2 Write the system boundary.** For RaviRide's ETA model, list what the system
decides, what it informs, and what it must never decide. Include one sentence on
who is harmed if each boundary is crossed.

**Check:** your table names a stage, not a person, and your boundary statement
distinguishes a prediction from a decision.

---

## Module 02 · Python, Git, CLI, environments

[Module 02 page](../modules/02-python-git-cli-environments/index.md) · [Lab](../modules/02-python-git-cli-environments/lab.md)

**2.1 Break the lock file two ways.** In a scratch project, (a) install a package
version that conflicts with a pin, and (b) remove a transitive dependency from the
lock file. For each, record the error, the command that revealed it, and the
recovery. Which failure was easier to diagnose, and why?

**2.2 Clone-and-run audit.** Clone your project into a new directory, delete the
virtual environment, and follow only the README. Keep a log of every command you
had to guess. Each guess is a documentation defect; fix the two worst.

**Check:** a second run of the audit needs no guesses, and `git status` is clean
apart from intended files.

---

## Module 03 · Project organization

[Module 03 page](../modules/03-project-organization/index.md) · [Lab](../modules/03-project-organization/lab.md)

**3.1 Draw the dependency direction.** List every module in `src/`, then draw an
arrow for each import. Any arrow that points from a pure module to an I/O module
is a design defect: move the I/O out or invert it with a parameter.

**3.2 Write a debt register with a budget.** Three items, each with: symptom,
cost per month (in hours), fix estimate, and a trigger for when it must be paid.
"No time" is not a trigger; "before the next release" is.

**Check:** no cycles in the import graph, and every debt item has a number.

---

## Module 04 · Data quality and versioning

[Module 04 page](../modules/04-data-quality-versioning/index.md) · [Lab](../modules/04-data-quality-versioning/lab.md)

**4.1 Add the check that would have caught it.** Take the corrupt batch from the
[module lab](../modules/04-data-quality-versioning/lab.md) and write one
additional check it would fail — a cross-column rule, not a range. Run the
validator before and after.

**4.2 Version a correction.** Fix one bad row in a copy of the dataset, commit the
correction as a new version, and show the diff between versions by row count and
by hash. Write two sentences on why the original must remain retrievable.

**Check:** the new check fails on the bad batch and passes on the good one, and
the old version still resolves.

---

## Module 05 · Reproducible training

[Module 05 page](../modules/05-reproducible-training/index.md) · [Lab](../modules/05-reproducible-training/lab.md)

**5.1 Prove stage-level invalidation.** Change one parameter that only `train`
declares, rerun, and paste the stage log. Then change a file that `prepare`
declares and rerun. Which stages ran, and why?

**5.2 Find the hidden input.** Deliberately add an undeclared read (a lookup CSV
loaded with a path relative to the working directory), run twice with different
contents, and observe the stale result. Add the file to `deps` and show the stage
rerunning.

**Check:** both runs produce the expected invalidation pattern, and the second fix
changes only the declaration.

---

## Module 06 · Experiment tracking

[Module 06 page](../modules/06-experiment-tracking/index.md) · [Lab](../modules/06-experiment-tracking/lab.md)

**6.1 Four runs, one table.** Train four configurations that differ in exactly one
parameter each, log them, and produce a table with parameter, metric, data
version, and run ID. Identify the configuration you would ship and the one you
would investigate.

**6.2 Find the weak slice.** For your best run, compute the metric by at least two
slices. Report the slice where it is worst, with its row count. If no slice is
worse, say so and explain what that implies about your slice choice.

**Check:** every number in the table traces to a run ID, and the weak slice has a
size.

---

## Module 07 · Testing ML systems

[Module 07 page](../modules/07-testing-ml-systems/index.md) · [Lab](../modules/07-testing-ml-systems/lab.md)

**7.1 Write a test that fails for the right reason.** Add a leakage test: shuffle
the target and assert the model's score falls to near chance. Run it, then
deliberately leak a target-derived feature and watch it fail.

**7.2 Test the API boundary.** Write five malformed-payload tests, each asserting
the status code, the field named in the error, and that no prediction is returned.
Then break the schema (remove `extra="forbid"`) and count how many fail.

**Check:** the leakage test fails when you leak, and the boundary tests name the
field rather than only the status.

---

## Module 08 · Pipeline automation

[Module 08 page](../modules/08-pipeline-automation/index.md) · [Lab](../modules/08-pipeline-automation/lab.md)

**8.1 One command, cold start.** Delete all generated outputs and run the pipeline
with one command. Record wall-clock time and the stages that ran. Run again
without changes and record the time. Explain the difference.

**8.2 Fail in the middle.** Inject a failure in stage 3 of 4, run, and record what
exists on disk afterwards. Is a partial output left behind that a later stage
could consume? Fix that if so.

**Check:** the second run skips everything, and a mid-pipeline failure leaves no
output that looks complete.

---

## Module 09 · Registry and lifecycle

[Module 09 page](../modules/09-model-registry/index.md) · [Lab](../modules/09-model-registry/lab.md)

**9.1 Block a candidate.** Register a model that fails one gate, attempt
promotion, and capture the error. Then fix the metric file and show promotion
succeeding. Which step would you not automate?

**9.2 Time a rollback.** Promote version B over A, then roll back to A and time it
from decision to a served prediction from A. Write the number down; it belongs in
the runbook.

**Check:** the blocked promotion names the failing gate, and the rollback has a
measured duration under five minutes.

---

## Module 10 · Serving

[Module 10 page](../modules/10-model-serving/index.md) · [Lab](../modules/10-model-serving/lab.md)

**10.1 Contract test.** Send the same row through the training feature path and
the API, and assert the predictions agree within 0.06 minutes. Then reorder the
serving feature list and watch the test fail while the API still returns 200.

**10.2 Failure modes.** Produce 422, 500, and 503 deliberately, and record the
response body and the log line for each. Which of the three should never be
reachable from a client error?

**Check:** the contract test distinguishes a wrong answer from a rejected one, and
no client error produces a 500.

---

## Module 11 · Docker

[Module 11 page](../modules/11-docker-containers/index.md) · [Lab](../modules/11-docker-containers/lab.md)

**11.1 Measure the layer cache.** Build the image, change one source file, rebuild,
and record the time. Then move the dependency install after the source copy,
rebuild from scratch, change the source again, and record the time. Explain the
difference.

**11.2 Shrink it honestly.** Compare the image with and without build tools in the
final layer, and with a slim base. Report size and start-up time, then state one
thing you chose not to optimise and why.

**Check:** the rebuild after a source change does not reinstall dependencies, and
the final image runs as a non-root user.

---

## Module 12 · CI/CD

[Module 12 page](../modules/12-ci-cd/index.md) · [Lab](../modules/12-ci-cd/lab.md)

**12.1 Three correct failures.** Inject, one at a time: a schema break, a unit
regression, and a metric regression. For each, capture the failing step and the
message. A failure that names the wrong step is a broken workflow.

**12.2 Least privilege.** Read your workflow's permissions and remove everything
not required. Then add a step that needs a permission you removed and observe the
failure. Restore only that permission.

**Check:** each injected defect fails the step that corresponds to it, and the
workflow has no `write-all`.

---

## Module 13 · Orchestration

[Module 13 page](../modules/13-orchestration/index.md) · [Lab](../modules/13-orchestration/lab.md)

**13.1 Justify the orchestrator.** Write a one-page decision record: what the
nightly job does, why a scheduled script is or is not sufficient, and what you
would have to add to a script to match the orchestrator's retry and history.

**13.2 Retry and backfill.** Force a task to fail twice, let the retry succeed,
then backfill a missed day. Record the run history and the duplicate-prevention
mechanism.

**Check:** the backfill does not duplicate rows, and the decision record names a
concrete cost of the orchestrator.

---

## Module 14 · Monitoring and drift

[Module 14 page](../modules/14-monitoring-drift/index.md) · [Lab](../modules/14-monitoring-drift/lab.md)

**14.1 Inject a shift.** Modify a batch's feature distribution, run your drift
check, and record which features flag. Then compute the model's accuracy on the
same batch *with labels*. Did accuracy fall? Report both facts separately.

**14.2 Write an actionable alert.** Define one alert with a threshold, an owner, a
first diagnostic step, and a condition for closing it. Test it against a normal
batch (should not fire) and a shifted one (should).

**Check:** the alert does not fire on the control batch, and the report separates
input drift from accuracy.

---

## Module 15 · Security and governance

[Module 15 page](../modules/15-security-governance/index.md)

**15.1 Threat-model one endpoint.** Four STRIDE categories, one threat each, one
mitigation, one residual risk. Then scan the repository for secrets and record
what the scan found, including "nothing".

**15.2 Write the limitations section first.** Before writing the model card's
performance section, write five limitations with the evidence for each. If you
cannot evidence a limitation, it is a guess; mark it as one.

**Check:** every threat has a residual risk, and every limitation has evidence or
an explicit "unverified".

---

## Module 16 · Cloud and Kubernetes

[Module 16 page](../modules/16-cloud-kubernetes/index.md)

**16.1 Local cluster, no cloud.** If a local cluster is available, deploy the
service with a Deployment, Service, readiness probe, and resource requests. Kill a
pod and observe recovery; roll out a new image and observe the strategy. If no
cluster is available, write the manifests and validate them with `kubectl apply
--dry-run=client`, then state what remains untested.

**16.2 Capacity estimate on paper.** From a measured per-pod throughput, compute
replicas for 50 requests per second with one-node-loss headroom. State every
assumption and the measurement that would falsify it.

**Check:** the manifests parse, the probe distinguishes liveness from readiness,
and the capacity number shows its arithmetic.

---

## Module 17 · Capstone

[Module 17 page](../modules/17-capstone/index.md)

**17.1 Clean-clone rehearsal.** Clone the repository to a new directory and follow
only the README to a working prediction. Time it. Every minute above 30 is a
documentation defect; fix the worst three.

**17.2 Incident drill.** Have someone inject one of the capstone faults (or use
the supplied script). Start a timer. Diagnose and restore, then write the
postmortem while the evidence is fresh.

**Check:** the clean clone reaches a prediction without questions, and the
postmortem names the detection gap, not only the cause.

---

## Recording your work

Keep one line per exercise in your portfolio:

```text
2026-10-26  M05 5.2  hidden input found (lookup.csv); fixed deps; rerun showed featurise+trained
2026-10-27  M12 12.1 schema break failed "validate data" at 41s; correct step
```

The date, the module, the exercise, and the evidence. A list of exercises you
"did" without evidence is a reading log, not a practice record.

---

## If an exercise does not work

| Symptom | Likely cause | Next step |
|---|---|---|
| The project has no `src/` yet | You are before Module 03 | Do the Module 03 lab first, or use a [starter project](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/starters) |
| A command from the module does not exist | Different project layout | The lab page has the exact path; this page assumes the course layout |
| Your metric differs from the module's | Different data seed or library version | Compare data hash and pins before assuming an error |
| No cluster, no Docker | Environment limitation | Do the paper version and label what is untested; that is assessed as honesty, not as a gap |

The exercises are deliberately independent of each other. If one blocks, move to
the next module's first exercise and come back with fresh eyes.

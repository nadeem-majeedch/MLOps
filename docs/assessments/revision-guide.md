# Final review and exam preparation

This page is for the last two weeks: consolidating seventeen modules, practising
the forms of assessment the course uses, and finding the gaps that reading cannot
hide. It is not a summary of the course. Summaries feel efficient and produce
recognition, which is not what an exam or an interview tests.

---

## 1. What is actually assessed

| Format | What it tests | How to practise |
|---|---|---|
| **Written or oral exam** | Mechanisms, trade-offs, and diagnosis under time pressure | Answer the [question banks](question-bank/index.md) aloud, without notes |
| **Practical assessment** | Whether you can make something work and prove it | Re-run a lab's fault and diagnosis with a timer |
| **Viva or defence** | Whether you understand your own system | Explain your capstone to someone who has not seen it |
| **Portfolio review** | Judgement and honesty over time | Read your own evidence as a sceptic |

Across all four, the same three things earn marks: the **mechanism** (how it
works), the **evidence** (how you know), and the **trade-off** (what it costs).
An answer with only the first is a definition. An answer with all three is what
distinguishes a pass from a strong pass.

---

## 2. The fourteen-day plan

Two hours a day, six days a week, with one rest day each week. Adjust to your
schedule, but keep the sequence: diagnosis before recall, practice before reading.

| Day | Focus | Work | Output |
|---|---|---|---|
| 1 | Reproducibility | Banks 02, then re-run MP1's clean clone | A list of every undocumented step you found |
| 2 | Data and leakage | Lab 03 diagnosis + Lab 07 leakage test | One new check you wrote |
| 3 | Evaluation | Bank 03 + your MP2 report | A slice you had not reported |
| 4 | Testing | Bank 04 + break one test deliberately | The failure output, kept |
| 5 | Serving | Bank 05 + five malformed payloads | The 422s and the fields they name |
| 6 | Rest | — | — |
| 7 | Containers | Lab 12 build/run, or the paper version | Size and start-time numbers |
| 8 | CI/CD | Bank 06 + three injected regressions | Three red logs |
| 9 | Orchestration | Bank 06 scenario + a retry/backfill | Run history with the retry |
| 10 | Monitoring | Bank 07 + inject a shift | Drift report and a control |
| 11 | Security | Bank 08 + secret scan | Scan output, findings explained |
| 12 | Cloud concepts | Bank 09 + capacity arithmetic | A number with assumptions |
| 13 | Integration | Capstone rehearsal: clean clone + incident drill | Timings and the postmortem |
| 14 | Rest and review | Read your weakest criterion; answer three scenarios aloud | One page of gaps |

If you have less than fourteen days, keep days 1, 3, 5, 8, 10, 13. Those cover the
failures that end projects: irreproducibility, dishonest evaluation, a broken
contract, a gate that does not gate, monitoring nobody can act on, and handover.

---

## 3. Topic map

| Topic | Read | Practise | Check yourself |
|---|---|---|---|
| Lifecycle and failure placement | [Module 01](../modules/01-introduction-to-mlops/index.md) | [Lab 01](../labs/lab-01-nondeterministic-analysis.md) | [Bank 01](question-bank/01-mlops-fundamentals.md) |
| Environments and Git | [Module 02](../modules/02-python-git-cli-environments/index.md) | [Lab 13](../labs/lab-13-dependency-conflict.md) | Bank 02 |
| Project structure | [Module 03](../modules/03-project-organization/index.md) | [Lab 02](../labs/lab-02-refactor-notebook.md) | Bank 02 |
| Data quality and versioning | [Module 04](../modules/04-data-quality-versioning/index.md) | [Lab 03](../labs/lab-03-data-defects.md), [Lab 04](../labs/lab-04-version-and-reproduce.md) | Bank 02 |
| Reproducible training | [Module 05](../modules/05-reproducible-training/index.md) | [Lab 05](../labs/lab-05-deterministic-pipeline.md) | Bank 02 |
| Tracking and evaluation | [Module 06](../modules/06-experiment-tracking/index.md) | [Lab 06](../labs/lab-06-experiment-comparison.md) | Bank 03 |
| Testing | [Module 07](../modules/07-testing-ml-systems/index.md) | [Lab 07](../labs/lab-07-leakage-tests.md) | Bank 04 |
| Automation | [Module 08](../modules/08-pipeline-automation/index.md) | [Lab 05](../labs/lab-05-deterministic-pipeline.md) | Bank 04 |
| Registry and lifecycle | [Module 09](../modules/09-model-registry/index.md) | [Lab 09](../labs/lab-09-release-candidates.md) | Bank 03 |
| Serving | [Module 10](../modules/10-model-serving/index.md) | [Lab 10](../labs/lab-10-serving-contract.md) | Bank 05 |
| Containers | [Module 11](../modules/11-docker-containers/index.md) | [Lab 12](../labs/lab-12-docker-image.md) | Bank 05 |
| CI/CD | [Module 12](../modules/12-ci-cd/index.md) | [Lab 14](../labs/lab-14-actions-workflow.md) | Bank 06 |
| Orchestration | [Module 13](../modules/13-orchestration/index.md) | [Lab 16](../labs/lab-16-scheduled-training.md) | Bank 06 |
| Monitoring and drift | [Module 14](../modules/14-monitoring-drift/index.md) | [Lab 17](../labs/lab-17-drift-analysis.md), [Lab 18](../labs/lab-18-regression-rollback.md) | Bank 07 |
| Security and governance | [Module 15](../modules/15-security-governance/index.md) | [Lab 19](../labs/lab-19-security-review.md) | Bank 08 |
| Cloud and Kubernetes | [Module 16](../modules/16-cloud-kubernetes/index.md) | Optional local cluster | Bank 09 |
| Whole lifecycle | [Module 17](../modules/17-capstone/index.md) | [Lab 20](../labs/lab-20-incident-review.md) | Capstone rubric |

---

## 4. Practice formats

### 4.1 The five-minute explanation

Pick a term — reproducibility, a quality gate, drift, a contract test — and
explain it to an imagined colleague in five minutes without notes. Then answer
"What would break if we skipped it?" and "What does it cost?" If you cannot name a
cost, you do not yet understand the trade-off.

### 4.2 Whiteboard the system

Draw the capstone from memory: data, training, registry, service, monitoring, and
the arrows between them. Then mark where each of these lives: the data hash, the
gate, the alert, the rollback. A diagram you cannot draw without notes is a map
you cannot use during an incident.

### 4.3 Trace a failure

Take one symptom and trace it backwards:

```text
Symptom: 2% of predictions are absurdly high
  -> Which layer could produce that?  service, features, model, artifact, data
  -> What evidence distinguishes them? logs, /model-info, feature values, training stats
  -> Which check should have caught it? schema, contract test, model test, gate
```

Do this for four symptoms: absurd values, a drop in one segment, 503s after a
deploy, and an alert nobody trusts.

### 4.4 Diagnose with a timer

Set 20 minutes. Take a fault from [Lab 20](../labs/lab-20-incident-review.md) or
inject one into your project. State a hypothesis before touching anything, gather
evidence, restore, and write three lines of postmortem. The timer is the point:
with unlimited time, everything is diagnosable.

### 4.5 Answer the scenario aloud

The Section D question in each bank is a rehearsal for a viva. Answer aloud, in
structure, in five minutes. Record it if you can bear to; you will hear the
moments where you substitute a list for a decision.

---

## 5. Quick reference

Facts that are easy to misremember under pressure. Each is explained in the
module linked above; this is a checklist, not a substitute.

### Contracts and status codes

| Situation | Response |
|---|---|
| Malformed body, wrong type, unknown field | 422 with the field named |
| Valid request, model not loaded | 503, retryable |
| Valid request, implausible output | 5xx with a specific message, and an alert |
| Unknown route | 404 |

### Versioning and caching

- A DVC stage key is built from the command, dependency hashes, declared
  parameters, and output hashes.
- An undeclared file is a hidden input; the stage will not rerun when it changes.
- A metrics file should be `cache: false` so it can be reviewed.
- Artifact bytes may differ between runs even when predictions agree: report
  behavioural determinism, not byte determinism.

### Evaluation

- Accuracy is misleading below about 10% prevalence; report PR AUC, recall at a
  chosen precision, and the confusion matrix.
- Choose the operating threshold before seeing test results.
- A slice needs a count; a difference on 4 rows is noise.
- A model that predicts the majority class is the floor, not a baseline to
  celebrate.

### Gates and releases

- A gate must fail the build, not warn.
- Pin the baseline by hash; a baseline regenerated by the same run checks nothing.
- Promotion is a policy applied to recorded metrics, not a memory of a good run.
- Rollback must be timed and the served version verified, not assumed.

### Monitoring

| PSI | Reading |
|---|---|
| < 0.10 | stable |
| 0.10–0.25 | watch |
| > 0.25 | act |

- Drift is a statement about inputs. Accuracy needs labels.
- A reference window that rolls nightly hides slow drift; freeze the training
  window and hash it.
- An alert needs an owner, a first diagnostic step, and a closing condition.

### Containers

- Copy dependency files before source to preserve the layer cache.
- Bind `0.0.0.0` inside the container, not `127.0.0.1`.
- Pin the base image; run as non-root; keep the artifact inside or document the
  mount.
- Health check proves the process; readiness proves it can serve.

### Kubernetes

- Requests affect scheduling; limits cap usage.
- Readiness gates traffic; liveness triggers restarts.
- A rolling update trades capacity for availability via `maxSurge` and
  `maxUnavailable`.
- `Pending` means unschedulable; read the events before changing anything.

---

## 6. Common mistakes

| Mistake | Why it loses marks | Do instead |
|---|---|---|
| Quoting a metric without its split | A number without a population is not evidence | Name the split, its size, and the positive rate |
| Saying "monitor accuracy" for a label-delayed system | Accuracy is unavailable when needed | Name the proxy signals and their limits |
| Treating drift as accuracy loss | Conflates inputs with outcomes | Separate the claims; state what labels would prove |
| "Add validation" as a fix | Names a category, not a check | Say what is validated, where, and what error results |
| Retraining as the response to every symptom | Retraining can hide a data defect | Diagnose first; name the evidence that would justify retraining |
| A gate that warns | Warnings are ignored | Fail the build or delete the check |
| Claiming Docker/Kubernetes was tested when it was not | Honesty gate | Label it untested and give the procedure |
| Removing a sensitive attribute and calling it fair | Bias persists in correlated features | Measure disparity and state the trade-off |

---

## 7. Last 24 hours

- [ ] Re-read your weakest rubric criterion and one module section behind it.
- [ ] Run the clean-clone command once; confirm the install still works.
- [ ] Answer one Section D scenario aloud, timed.
- [ ] Read your capstone's limitations section; be ready to defend each line.
- [ ] Prepare three numbers you can explain: a metric with its split, a latency
      with its method, a rollback time with its evidence.
- [ ] Prepare one thing that does not work, and what you would do next.
- [ ] Sleep. A rested recall of mechanisms beats another hour of reading.

---

## 8. After the assessment

Write three paragraphs while it is fresh: what you knew cold, what you
misremembered, and what you would build differently. Keep them with your
portfolio. The next interview will ask the same questions in a different order,
and the third paragraph is the one that makes your answers specific.

If you are continuing to the capstone, go back to the
[capstone assessment](capstone-assessment.md) and score the artefact you are least
confident about first.

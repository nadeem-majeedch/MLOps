# Guided lab · Build it, hand it over, then break it

**Time:** 30+ hours over four to six weeks (Core), 40+ hours (Full). **Tools:** those from Modules 02–16; nothing new. **Cost:** free and local. No cloud account is required.

## Scenario and business problem

RaviRide's ETA service has grown module by module: a pipeline, a registry, an API, a container, CI, a scheduler, and a monitor. Each piece works in the module that introduced it. Nobody has run the whole thing from a clean copy, and nobody else has operated it.

You are the engineer handing it over. The handover is the exam: can a peer deploy it from your documentation, can your gates stop a bad release, and can you diagnose a fault you did not choose?

This lab is the capstone itself. It is guided in sequence, not in solution: the artefacts are specified, the evidence is required, and the decisions are yours.

### Skills practised

- Scoping a system and writing down what it must not do.
- Reproducing a pipeline from a clean clone, with a stated tolerance.
- Making data, model, and API tests that fail for the right reason.
- Serving, containerising, and gating a release.
- Monitoring, deciding, rolling back, and writing a postmortem.
- Handing over to a peer and defending the design.

### Prerequisites

Modules 01–07, 09–12, and 14 complete. Modules 13, 15, and 16 are required for the Full variant and optional for Core. You need a repository you can clone, a working environment, and 30+ hours.

### Inputs

| Input | Source |
|---|---|
| RaviRide project | `examples/raviride/` or your own module work |
| Synthetic data | `python scripts/generate_trips.py --out data/raw/trips.csv` |
| Incident evidence (rehearsal) | `examples/labs/lab-20-incident/incident.py` |
| Starter reference | `examples/starters/advanced-monitoring-pipeline/` |
| Brief and rubric | [Capstone brief](../../projects/capstone.md) · [Assessment framework](../../syllabus/assessment-framework.md#5-component-4-capstone-40) |

Do not use real student, customer, or personal data. The course data is synthetic.

## Phase 0: scope and boundary (3 hours)

1. Write `docs/scope.md`: the decision the prediction changes, the user, the input, the output, the out-of-scope list, and the failure that matters most.
2. Write the smallest useful version in one paragraph. If it includes a new tool, remove the tool or justify it.
3. Choose Core or Full. Write the choice and the reason.
4. Create the handover skeleton from the brief:

   ```text
   capstone/
   ├── README.md
   ├── docs/{architecture,runbook,model-card,postmortem}.md
   └── evidence/{ci,drift,rollback}/
   ```

**Checkpoint 0:** a reader can say what the system does, who it is for, and what it must not do, without opening the code.

## Phase 1: clean-clone pipeline (8 hours)

5. From a clean copy, follow only your README. Record every undocumented step; each is a defect to fix.
6. Generate the data, run the pipeline, and record the metric and the wall-clock time.
7. Record the data hash, the model version, the commit, and the parameters. Put them in `docs/architecture.md` as a lineage chain.
8. Add a `Makefile` or a single entry command if the README has more than six steps. Reduce the steps until a peer can follow them.
9. Run the clean clone a second time. The metric should be within your stated tolerance; byte-identical artifacts are not required unless you have eliminated every source of variation.

**Checkpoint 1:** a clean clone reaches the reported metric within tolerance, following the README only. Record the time.

*Reference values:* the course project's baseline MAE is about 2.77 on its test split; the exact number depends on the data version and library versions. State your tolerance, for example ±0.05.

## Phase 2: tests and a gate that fails (8 hours)

10. Ensure you have data validation, unit tests, a model-quality test, and an API contract test. The course project has ten API tests; yours should cover the same failure classes.
11. Inject three regressions, one at a time:
    - **schema**: rename or retype a field the model expects;
    - **unit**: change a feature from kilometres to miles, or change a category mapping;
    - **metric**: train a deliberately weak model, or corrupt one slice.
12. For each, run the gate and keep the failing output and exit code in `evidence/ci/`. Restore the code after each.
13. Confirm the gate passes on the restored code. A gate that has never passed is as suspect as one that has never failed.

**Checkpoint 2:** three failing runs, each for the stated reason, plus one green run. The failure messages name the artefact.

## Phase 3: serve and containerise (7 hours)

14. Serve the champion with a validated contract. Send five malformed requests and record the status and message:
    - unknown zone;
    - negative distance;
    - missing field;
    - extra field;
    - wrong type or out-of-range value.
15. Build the image and run it with the model baked in or mounted. Confirm `/health`, `/ready`, and `/predict`.
16. Add a container test or a smoke test that runs in CI. It should fail if the image cannot start or the model is missing.

**Checkpoint 3:** five 422s with specific messages, a running container, and a smoke test.

## Phase 4: monitor and decide (6 hours)

17. Log predictions without personal data. Include a join key, the model version, and a timestamp.
18. Produce a drift report for a later batch. Use the course monitor or your own PSI implementation.
19. Configure one alert with an owner, a threshold, and a first diagnostic step. Test it with a known shifted batch.
20. Write the retraining decision rule: what evidence, how many windows, which gate, who approves. It must not be "retrain when drift is high".

**Checkpoint 4:** the alert fires on the injected batch, names an owner, and the decision rule is executable.

## Phase 5: handover (5 hours)

21. Write the runbook: deploy, rollback, the top three alerts, and the first five checks for each.
22. Write the model card: intended use, prohibited use, data, evaluation, limitations, disparity (if measured), monitoring, owner.
23. Ask a peer who has not seen the project to deploy from the runbook. Time it. Do not answer questions during the attempt; write down every question afterwards and fix the documentation.
24. Record the peer's time and the questions in `evidence/handover.md`.

**Checkpoint 5:** a peer deploys in under 30 minutes, or you have a list of the gaps and a plan to close them.

## Phase 6: the incident simulation (4 hours)

25. Use the supplied incident pack or inject a fault into your own system without looking at the cause. Start a timer.
26. Follow the incident process: declare, stabilise, hypothesise, gather evidence, restore, review.
27. Diagnose within 30 minutes if you can. Record the timeline, the first hypothesis, the evidence that confirmed or rejected it, and the restoration signal.
28. Write `docs/postmortem.md` with the eight sections: Summary, Impact, Timeline, Root cause, Detection, Response, Prevention, Lessons. Blameless language; no individual named as the cause.
29. Run the incident checker if you used the supplied pack:

    ```bash
    cd examples/labs/lab-20-incident
    python incident.py
    python check_lab20.py
    ```

    Expected: `34/34 checks passed`, 660 failed requests, MTTR 128 minutes.

**Checkpoint 6:** the postmortem's claims match the evidence pack, and the prevention items are verifiable.

## Phase 7: defence and portfolio (3 hours)

30. Write the defence document: what the system does, what it does not, the decision you would change, why not simpler, what breaks at 10× load, the top residual risk.
31. Write the 400–600 word portfolio narrative from the [capstone brief](../../projects/capstone.md#10-portfolio-narrative).
32. Do a 15-minute timed defence with a peer or record yourself. Answer without opening the code.

**Checkpoint 7:** the defence names a trade-off, a bottleneck, and a residual risk, each with evidence.

## Expected outputs

| Artefact | Reference |
|---|---|
| Clean clone | Metric within stated tolerance; time recorded |
| Lineage | Alias → version → run → data hash → commit |
| Gate | 3 failing runs + 1 green, output retained |
| API | 5 malformed requests, specific 422s |
| Container | `/health`, `/ready`, `/predict` verified |
| Alert | Fires on the shifted batch; owner and first step named |
| Handover | Peer deploy time under 30 minutes |
| Incident | Diagnosed within 30 minutes; postmortem complete |
| Defence | "Why not simpler?" and "10× load" answered with specifics |

## Acceptance criteria

| # | Criterion | Passes when |
|---|---|---|
| 1 | Scope | Decision, user, input, output, out-of-scope, worst failure |
| 2 | Clean clone | Stranger reproduces the metric from the README |
| 3 | Provenance | Chain complete; any `unknown` explained |
| 4 | Gate | Fails for the right reason on schema, unit, and metric |
| 5 | Evidence | Failing output and exit codes retained |
| 6 | Contract | Five 422s with actionable messages |
| 7 | Container | Runs and serves; smoke test exists |
| 8 | Monitoring | Alert with owner, threshold, first step |
| 9 | Decision rule | Evidence-based, with an approver |
| 10 | Rollback | Demonstrated and timed under five minutes |
| 11 | Handover | Peer deploys from the runbook in under 30 minutes |
| 12 | Incident | Timeline, hypothesis, evidence, restoration, postmortem |
| 13 | Model card | Intended use, prohibited use, two specific limitations |
| 14 | Defence | Trade-off, bottleneck, residual risk, all specific |
| 15 | Honesty | What was not tested is stated |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Clean clone fails at the first command | Undocumented prerequisite or a path relative to your machine | Add the prerequisite and use repository-relative paths |
| Metric differs beyond tolerance | Different data version, library version, or seed | Pin versions, record the data hash, state the tolerance |
| Gate passes a regression | The test does not exercise the changed path | Make the regression observable at the contract or metric level |
| Gate fails for the wrong reason | Missing fixture, import error, or environment | Fix the test harness before trusting a red run |
| API returns 500 on bad input | Validation is missing or the error is unhandled | Add the schema rule and a test for the 422 |
| Container starts but `/ready` fails | Model path or registry URI differs in the image | Bake the artifact or set the URI explicitly; test in the image |
| Alert never fires | Threshold too high, reference stale, or batch too small | Inject a known shift; check row counts and reference |
| Peer cannot deploy | Runbook assumes your environment | Watch them, write down every question, fix the doc |
| Incident diagnosis runs long | No hypothesis, or no timeline of changes | Stabilise first; write the hypothesis before investigating |
| Postmortem is rejected as blaming | "The engineer should have..." | Rewrite as a system condition with a control |

## Reflection questions

1. Which artefact took longer than you expected, and what does that say about the estimate?
2. Which gate would you keep if you could keep only one, and what would you lose?
3. What did your peer ask that you thought was obvious?
4. What would you cut if you had half the time?
5. What is the top residual risk, and what would you monitor for it?
6. What would break first at 10× load, and what is the evidence?

## Optional extension

Take the Full variant: add orchestration with retries (Module 13), a threat model and dependency scan (Module 15), and a local cluster deployment with probes and limits (Module 16). The extension is assessed on the same seven artefacts plus the cross-cutting criteria; it is not a different rubric.

## Cleanup

Keep the repository, the evidence, the runbook, the model card, and the postmortem; they are the portfolio. Remove generated data and artifacts only after you have recorded their hashes and the metric.

```bash
rm -rf data/processed data/features models mlruns .pipeline logs
rm -rf examples/labs/lab-20-incident/incident examples/labs/lab-20-incident/artifacts
```

PowerShell:

```powershell
Remove-Item data\processed, data\features, models, mlruns, .pipeline, logs -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item examples\labs\lab-20-incident\incident, examples\labs\lab-20-incident\artifacts -Recurse -Force -ErrorAction SilentlyContinue
```

Do not delete a cluster, registry, or cloud resource you did not create.

## Checklist

- [ ] Scope and out-of-scope are written
- [ ] A clean clone reproduces the metric within tolerance
- [ ] Lineage is complete, or every gap is explained
- [ ] The gate fails for schema, unit, and metric reasons
- [ ] Failing and green CI output is retained
- [ ] Five malformed requests return specific 422s
- [ ] The container serves and has a smoke test
- [ ] The alert has an owner and a first diagnostic step
- [ ] Rollback is demonstrated and timed
- [ ] A peer deployed from the runbook in under 30 minutes
- [ ] The incident was diagnosed and a blameless postmortem written
- [ ] The model card states intended use, prohibited use, and two limitations
- [ ] The defence answers "why not simpler?" and "10× load"
- [ ] The portfolio narrative is 400–600 words

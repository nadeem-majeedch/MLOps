# Final project report template

> Copy this into `docs/report.md` at submission. Four to eight pages, plus
> appendices. The reader is a competent engineer who has not seen your project and
> has twenty minutes.

---

# *Project title*

**Author**, **date**, **course/module**, **repository link**

---

## 1. Summary (150 words)

*What the system does, for whom, what it achieves, and what it does not do. A
reader who stops here should know whether to keep reading.*

## 2. Problem and success criteria

*Condensed from the [problem statement](problem-statement.md). Include the table of
criteria and whether each was met.*

| Criterion | Target | Achieved | Evidence |
|---|---|---|---|
| MAE | ≤ 3.0 min | 2.9 | `evidence/metrics.json` |
| Long-trip MAE | ≤ 4.0 | 3.8 | same |
| p95 latency | ≤ 150 ms | 84 ms | `evidence/latency.txt` |
| Rollback | ≤ 5 min | 2 min 40 s | `evidence/rollback.log` |

## 3. Data

| | |
|---|---|
| Source and licence | |
| Rows, period, target | |
| Sensitive fields | |
| Validation rules | *list the rules, not "validated"* |
| Known limitations | |

*Two or three sentences on what the data cannot support. Synthetic data cannot
support claims about real traffic; say so here, not in a footnote.*

## 4. Method

*What you built, in the order it runs. Reference the
[architecture](architecture-diagram.md) rather than repeating the diagram.*

- **Features**: list, and one sentence on why each is legitimate.
- **Model**: choice, parameters, and the alternative you rejected.
- **Split**: how leakage was prevented, and the evidence.
- **Threshold**: how it was chosen and when.

## 5. Evaluation

| Metric | Baseline | Final | Notes |
|---|---|---|---|
| MAE | | | |
| Long-trip MAE | | | |
| p95 error | | | |

### Slices

| Slice | Rows | MAE | Note |
|---|---|---|---|
| | | | |

### What the evaluation does not show

*At least two limits: synthetic data, a single split, no A/B test, no fairness
analysis on real groups.*

## 6. Engineering

| Area | What exists | Evidence |
|---|---|---|
| Reproducibility | Pinned env, DVC stages, clean-clone run | `evidence/clean-clone/` |
| Tests | 63 tests, five layers | `docs/test-evidence.md` |
| CI gate | Metric floor, three injected failures | `evidence/ci/` |
| Serving | FastAPI, validation, `/model-info` | `evidence/serving/` |
| Container | Pinned, non-root, artifact inside | `evidence/container/` |
| Monitoring | Input, prediction, outcome signals | `docs/monitoring/` |
| Rollback | Demonstrated and timed | `evidence/rollback/` |

## 7. Operations

*One page: how it is deployed, how it is monitored, how it is rolled back, and what
happens when the alert fires. Link the runbook rather than duplicating it.*

| Scenario | Detection | First action | Owner |
|---|---|---|---|
| Model missing at start-up | `/ready` 503, crash loop | Check artifact mount | Service |
| Input drift | PSI alert | Check the cause before retraining | Data |
| Accuracy drop | Matured-label metric | Compare slices, open candidate | ML |
| Bad release | Error rate or smoke failure | Roll back, keep logs | Service |

## 8. Security, privacy, and governance

- Secret scan result and how findings were handled.
- Data provenance and licence.
- Personal data: none, or the legal basis and minimisation.
- Fairness: what was measured, on which groups, with which caveat.
- Residual risk, named.
- Model card link.

## 9. Limitations

*The section that most distinguishes a strong report. Five items, each with
evidence or an explicit "unverified".*

1. Synthetic data: the relationships are simpler than real traffic.
2. Single temporal split: no estimate of performance across seasons.
3. No A/B test: offline improvement may not translate.
4. Fairness measured on synthetic zones, not on protected groups.
5. Docker image built but not run in the authoring environment (if true).

## 10. What I would do next

*Three items, ordered by value, with the evidence that justifies each. "Add more
tests" is not one; "add a test that fails when the zone encoding changes, because
that defect appeared twice" is.*

## 11. Reflection

*Half a page. Which decision are you least confident about? What would change your
mind? What did you learn that you could not have learned by reading?*

---

## Appendices

| Appendix | Contents |
|---|---|
| A | Commands to reproduce from a clean clone |
| B | Full metric tables and plots |
| C | Experiment records |
| D | Incident postmortem |
| E | Model card |
| F | Runbook |

---

## Checklist

- [ ] Summary states what it does *and* does not do.
- [ ] Every success criterion has an achieved value and evidence.
- [ ] Data licence and limitations are stated.
- [ ] Evaluation includes at least two slices with counts.
- [ ] Engineering claims point to evidence files.
- [ ] Operational scenarios have an owner and a first action.
- [ ] Limitations include at least one thing that was not tested.
- [ ] Next steps are specific and justified.
- [ ] The appendix commands work from a clean clone.
- [ ] No secret, personal data, or absolute path appears anywhere.

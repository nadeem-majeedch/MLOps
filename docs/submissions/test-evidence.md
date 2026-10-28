# Test evidence template

> Copy this into `docs/test-evidence.md` when your suite and gate exist. The
> purpose is to show what is checked, what happens when it is broken, and what
> remains unchecked.

---

## 1. Summary

| | |
|---|---|
| **Test command** | `python -m pytest` |
| **Suite runtime** | *42 s* |
| **Tests** | *63 passed, 0 skipped* |
| **Coverage** | *81% of `src/`, if measured* |
| **CI workflow** | `.github/workflows/ci.yml`, run #128 |
| **Last verified** | YYYY-MM-DD, on *OS and Python version* |

## 2. What each layer checks

| Layer | Examples | Defect it catches | Count |
|---|---|---|---|
| Unit | Distance conversion, threshold logic | Arithmetic and boundary errors | 24 |
| Data | Required columns, nulls, ranges, duplicates | A bad batch before training | 12 |
| Model | MAE floor, slice floor, invariance to `trip_id` | A model that regressed or learned an ID | 9 |
| Contract | Serving features vs training features | Skew that returns plausible wrong answers | 6 |
| Integration | Pipeline end to end on a fixture | Wiring and artefact-name mistakes | 5 |
| Regression | Known-good predictions within tolerance | Silent behaviour change | 7 |

## 3. Proof that the tests can fail

For each important test, record a deliberate break and the failure it produced.
This is the section that distinguishes a real suite from a green tick.

| Test | Deliberate break | Observed failure | Kept at |
|---|---|---|---|
| `test_no_leakage` | Shuffled target, then leaked a target-derived feature | `AssertionError: AUC 0.94 on shuffled labels` | `evidence/ci/leak-test.log` |
| `test_contract_matches_training` | Reordered serving feature list | `assert 18.4 == 24.1` | `evidence/ci/contract.log` |
| `test_schema_rejects_unknown_field` | Removed `extra="forbid"` | `DID NOT RAISE` | `evidence/ci/schema.log` |
| `test_metric_floor` | Trained on 5 rows | `MAE 9.8 > ceiling 3.5` | `evidence/ci/gate.log` |

## 4. The gate

| | |
|---|---|
| **What it blocks** | A model whose MAE exceeds 3.5 min, or whose long-trip MAE exceeds 4.5 |
| **Baseline** | `metrics/baseline.json`, hash `a1b2…` |
| **Where it runs** | CI step `metric-gate`, after tests and data validation |
| **Exit behaviour** | Non-zero, with the failing metric printed |
| **Last red run** | *link or path* |
| **Last green run** | *link or path, after the fix* |

*If the gate has never failed, it has not been tested. Inject a regression and
keep the log.*

## 5. What is not tested

| Gap | Why | Risk | Mitigation |
|---|---|---|---|
| Docker build | Docker unavailable in the environment | Image may not start | Dockerfile linted; commands documented; labelled untested |
| Kubernetes rollout | No cluster | Probes may be misconfigured | `--dry-run=client` validation only |
| Real traffic latency | No production access | p95 may exceed budget | Synthetic load test at 20 rps |
| Fairness on real groups | Synthetic data only | Disparity unknown | Measured on synthetic slices; stated as a limitation |

*An empty table here is almost certainly wrong. Name the gaps.*

## 6. Running it yourself

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python scripts/check_metrics.py
```

Expected: all tests pass; the metric check prints `PASS` and exits 0. To see a
failure, run `python scripts/inject_defect.py --kind schema` and repeat.

---

## Checklist

- [ ] The command and its runtime are stated.
- [ ] Each layer has at least one test and a named defect it catches.
- [ ] At least three tests are shown failing for the right reason.
- [ ] The gate's baseline is pinned by hash.
- [ ] Both a red and a green gate run are kept.
- [ ] Untested areas are named with a risk and a mitigation.
- [ ] Running the suite from a clean clone works.

# Guided lab · Register three candidates, block one, roll one back

**Time:** 5 hours. **Tools:** Python 3.11/3.12, scikit-learn, MLflow 2.x with a local file store, Git. No server, no account, no cloud storage.

## Scenario and business problem

RaviRide's release process is a group chat. Someone trains a model, posts the MAE, and if nobody objects it is copied to the serving machine. Last month a model with a better average error shipped and complaints rose from one zone; nobody could prove which model was live, or which data it had seen.

You will replace the group chat with a registry: immutable versions, an alias that names the live model, gates that decide eligibility, and a rollback you have actually rehearsed.

### Skills practised

- Logging a model with a signature and an input example.
- Registering versions and moving an alias.
- Writing gates as code: absolute, relative, slice, and provenance.
- Diagnosing a blocked candidate without loosening the gate reflexively.
- Rehearsing a rollback and timing it.
- Tracing lineage from alias to dataset hash.

### Prerequisites

Modules 06 (MLflow tracking) and 08 (a working pipeline). You need `data/features/{train,test}.csv` and a fitted model.

### Input data

The feature files from your pipeline: 896 training rows and 304 test rows. No downloads. The registry itself is generated state under `mlruns/`, ignored by Git.

### Directory layout you will build

```text
raviride-eta/
├── registry/
│   ├── registry.py            # train, gate, promote, rollback, show
│   ├── promotion_policy.yaml
│   └── smoke_test.py
├── candidates/                # one JSON per candidate, ignored by Git
├── mlruns/                    # local tracking + registry store, ignored
└── docs/promotion-evidence.md
```

## Part 1: register a baseline (45 minutes)

1. Install and pin MLflow in your environment, then record the version:
   ```powershell
   python -m pip install "mlflow==2.17.2"
   python -c "import mlflow; print(mlflow.__version__)"
   ```
   **Checkpoint 1:** the version prints and `mlruns/` is in `.gitignore`.
2. Point the tracking URI at a project-local store *before* any logging:
   ```python
   mlflow.set_tracking_uri((ROOT / "mlruns").as_uri())
   ```
3. Write `train(name, overrides)` that fits the pipeline, computes overall and per-zone MAE, logs parameters, tags (`data_hash`, `git_commit`, `candidate`), metrics, and the model:
   ```python
   signature = infer_signature(example, model.predict(example))
   mlflow.sklearn.log_model(model, artifact_path="model",
                            signature=signature, input_example=example)
   ```
4. Register it: `mlflow.register_model(f"runs:/{run_id}/model", "raviride-eta")`.
   **Checkpoint 2:** the run has a signature, an input example, and a data hash tag; the version number is `1`.

*Recovery:* if the model logs without a signature, `input_example` was `None` or the wrong shape. Three rows of the exact feature frame is enough.

## Part 2: three candidates, one policy (75 minutes)

5. Train two more candidates with deliberately different behaviour:
   - a deeper forest (more trees, greater depth);
   - a deliberately weak one (very shallow, large leaves).
6. Write `promotion_policy.yaml` with an absolute ceiling, a relative regression limit, and per-zone limits. Give the sparse zones more room and write a comment saying why.
7. Implement `gates(version)` returning `(ok, reasons)`. Every reason must include the candidate value, the limit, and the comparison baseline.
   **Checkpoint 3:** `gate 3` on the weak candidate prints at least three reasons, and each is reproducible by hand from the logged metrics.

8. Promote the baseline with no champion present; confirm the alias:
   ```powershell
   python registry/registry.py promote 1
   python registry/registry.py show
   ```
   **Checkpoint 4:** `show` marks version 1 with `champion`.

## Part 3: find the candidate that looks best and is not (60 minutes)

9. Gate the deeper candidate. If it passes, promote it and record why. If it fails, record which slice and by how much.
10. Create a candidate that changes *one* thing with a plausible justification — for example, dropping a zone's rows as outliers, or removing a feature to simplify the service. Register it.
11. Gate it. Answer in `docs/promotion-evidence.md`:
    - Which number improved?
    - Which number got worse, and for which population?
    - How many test rows support the worse number?
    - Would you ship it? Defend the answer in three sentences.
    **Checkpoint 5:** you have at least one blocked candidate and a written defence, not just a rejection.

*Recovery:* if every candidate passes, your tolerances are too loose to be meaningful. Tighten the relative limit until the difference between candidates is visible, and record the change.

## Part 4: promote and smoke-test (30 minutes)

12. Promote the candidate you would ship. Record the previous champion from the output (`was vN`).
13. Write `smoke_test.py` that loads `models:/raviride-eta@champion`, predicts one fixed trip, and fails when the prediction leaves a stated range.
    **Checkpoint 6:** the smoke test passes on the champion, and fails when you temporarily point it at the deliberately weak version.

*Note:* a smoke test proves the artifact loads and produces a plausible number. It does not prove quality — the reference run's smoke test passed on a model that should not have shipped.

## Part 5: rehearse the rollback (30 minutes)

14. Pretend the promotion was a mistake. Time the rollback:
    ```powershell
    Measure-Command { python registry/registry.py rollback }
    ```
15. Confirm the alias, the smoke test, and the recorded `rollback_at` tag.
16. Write down: elapsed time, the exact command, what the rollback fixed, and three things it did not fix.
    **Checkpoint 7:** the alias is back on the previous version and the evidence file contains a measured time, not an estimate.

## Part 6: lineage and a policy change (45 minutes)

17. Produce a lineage trace for the current champion: alias → version → run → `data_hash` → `git_commit` → params. Put it in the evidence file as a table.
18. Add one **provenance** gate justified by something you observed (for example: no production zone may be missing from training; the dataset hash must be present; the commit must not be `unknown`).
19. Re-gate the candidate that passed before your policy change. Record whether it still passes.
    **Checkpoint 8:** you can show a candidate whose eligibility changed because the policy changed, and explain why that is correct rather than unfair.

20. Commit `registry/`, `promotion_policy.yaml`, and the evidence file. Do not commit `mlruns/` or `candidates/`.

## Expected outputs

| Output | Reference value |
|---|---|
| Versions | 6 registered; `champion` moved v1 → v2 → v5 → rollback to v2 |
| Weak candidate | 6 gate failures, MAE 3.442 against a 3.20 ceiling |
| Best-aggregate candidate | MAE 2.7275, blocked on Z07 (5.512 vs 5.179, limit 5%) |
| Provenance gate | `training data excludes production zones: Z08` |
| Rollback | 2.1 s end to end; 25 ms for the alias write |
| Lineage | `data_hash=285bbf8406f483a9`, `git_commit=ac4246f`, `train_rows=896` |

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Artifact | Loads without importing the training package; has signature and input example |
| Versions | Immutable; old versions keep their metrics when the alias moves |
| Gates | At least three families (absolute, relative, slice or provenance), each machine-evaluable |
| Blocked log | Names the candidate, the gate, the values, and the limit |
| Rollback | Rehearsed, timed, and followed by a smoke test |
| Lineage | Complete from alias to commit; no `unknown` fields you could have filled |
| Honesty | The evidence file states what the local registry does not protect against |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `RESOURCE_DOES_NOT_EXIST` on alias | Model name typo, or a different tracking URI | Check `mlflow.get_tracking_uri()` in the same process |
| Version numbers keep increasing in tests | Every run registers a new version | Expected; use a scratch experiment or a test model name |
| `get_model_version_by_alias` fails | MLflow older than the aliases API | Use 2.x; stages are deprecated, do not fall back to them |
| Model loads but metrics are missing | Metrics logged to a different run | The version stores its `run_id`; query that run |
| Signature error on load | Feature frame column order differs | Use the stored `feature_columns`, not a hand-built list |
| Promotion "succeeds" but serving still returns old predictions | The server caches the model in memory | Reload/restart; Module 10 discusses this |
| Rollback command prints `no previous champion` | `promoted_from` missing on the first promotion | Pass `--to VERSION` explicitly |

## Cleanup

- Keep `mlruns/` locally for inspection; it is ignored by Git. It grows slowly at this scale.
- Remove the scratch candidates you do not reference in the evidence file.
- No services were started, so nothing needs stopping.
- If you experimented with a remote registry, verify no credentials were written into the repository.

## Optional extensions

1. **Challenger alias.** Keep `challenger` pointing at the best rejected candidate and add a gate that compares it to `champion` on demand. Explain what a shadow deployment would add that the alias does not.
2. **Two-key promotion.** Require a `approved_by` tag set by a second person before `promote` succeeds, and demonstrate the failure when it is missing. Discuss how you would prevent self-approval in a real system.
3. **Schema check at load.** Before predicting, assert that the loaded model's signature matches the feature frame's dtypes. Break one dtype deliberately and record the error.

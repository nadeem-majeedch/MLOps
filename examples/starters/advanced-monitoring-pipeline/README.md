# Advanced starter — validated pipeline, gated registry, drift monitor

A small but complete lifecycle: schema checks, a group-aware split, a model whose
operating threshold is chosen before test, a local registry with a promotion
policy, and a drift report for a later batch. It is the closest of the three
templates to the capstone, and the one whose failures are most interesting.

| | |
|---|---|
| **Level** | Advanced |
| **Task** | Imbalanced binary classification (failure within 7 days) |
| **Data** | Synthetic, generated locally; a labelled reference and an unlabelled later batch |
| **Time to run** | About two minutes |
| **Needs** | Python 3.11+; no service, no account |

---

## What it demonstrates

- **Group splitting.** Readings from one machine never appear on both sides.
  A random split is available in one line and inflates the metric; the README
  asks you to measure the difference.
- **A recall target, not a probability cutoff.** The threshold is the quantile of
  training positive scores that reaches 80% recall, frozen before test.
- **A promotion policy applied to recorded metrics**, with every blocking reason
  printed. Promotion is code, not convention.
- **Rollback** to the previous version, in one command.
- **PSI drift** on inputs, with the honest caveat that it says nothing about
  accuracy without labels.
- **CI as exit codes**: `cli.py` returns 0, 1 (validation or gate), or 2 (drift).

What it does not demonstrate: authentication, a real registry service, artifact
storage, concurrency, or alerting. Each is named in the module that covers it.

---

## Layout

```text
advanced-monitoring-pipeline/
├── cli.py                       # validate | train | promote | monitor | rollback | all
├── make_data.py                 # reference data + a shifted, unlabelled batch
├── configs/pipeline.yaml        # policy and drift thresholds
├── .github/workflows/quality.yml
├── requirements.txt
├── pytest.ini
├── data/                        # generated
├── artifacts/                   # model, metrics, run_meta, registry/registry.json
├── src/pipeline/
│   ├── data.py                  # validation, group split
│   ├── model.py                 # scaled logistic, threshold selection, metrics
│   ├── registry.py              # versions, champion alias, gate, rollback
│   └── drift.py                 # PSI, bands, report
└── tests/
    ├── test_data.py
    ├── test_model.py
    ├── test_registry.py
    └── test_drift.py
```

---

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python make_data.py
python -m pytest
python cli.py validate
python cli.py train
python cli.py promote --note "baseline"
python cli.py monitor
echo $?          # 2: drift was found
```

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python make_data.py
python -m pytest
python cli.py validate
python cli.py train
python cli.py promote --note "baseline"
python cli.py monitor
$LASTEXITCODE    # 2: drift was found
```

### Expected output

```text
$ python make_data.py
wrote data/equipment.csv      480 rows  37 positive
wrote data/current_batch.csv  160 rows  unlabelled, shifted

$ python -m pytest
29 passed

$ python cli.py train
train rows  360  machines ['M01', 'M02', 'M03', 'M04', 'M05', 'M06']
test        120 rows  held out ['M07', 'M08']
roc_auc     0.8382
pr_auc      0.4268
recall      0.8750 at threshold 0.0731 (chosen for 80% train recall)
precision   0.1707
confusion   tp=7 fn=1 fp=34

$ python cli.py promote --note baseline
registered version 1 and promoted it to champion

$ python cli.py monitor
temperature_c          PSI  0.781  drift   mean 68.72 -> 74.32
vibration_mm_s         PSI  3.216  drift   mean 2.35 -> 3.2
pressure_bar           PSI  0.128  watch   mean 4.2 -> 4.18
operating_hours        PSI  0.058  stable  mean 4556.29 -> 4527.48
days_since_service     PSI  1.446  drift   mean 106.61 -> 143.76
verdict     drift
ALERT: input distribution moved. Find the cause before retraining.
drifted: days_since_service, temperature_c, vibration_mm_s
```

Precision of 0.17 means 34 false alarms for every 7 true ones. That is a
deliberate trade: with 8% prevalence and a missed failure far more expensive than
an inspection, recall is the constraint. Write the trade-off down; do not quote
accuracy.

`cli.py all` runs every stage and ends with the monitor's exit code, so on this
data it exits **2** even though training and promotion succeeded. That is the
intended behaviour, and the CI workflow treats drift as evidence rather than a
failed build.

---

## What the drift report does and does not say

It says the readings in the later batch have higher vibration, higher
temperature, and more days since service. That is consistent with a maintenance
interval being extended, which is a real operational cause worth checking before
blaming the model.

It does **not** say accuracy fell. The batch has no labels — nobody knows yet
which machines failed. To learn that, you would need:

1. outcomes observed for these machines after seven days;
2. a labelled holdout from the same period;
3. the same metric, computed on that holdout, against the frozen threshold.

Until then, "the inputs moved" is the whole claim. Module 14 explains why
conflating the two leads teams to retrain during an outage.

---

## Read the code in this order

1. `src/pipeline/data.py` — `validate()` and `split_by_machine()`.
2. `src/pipeline/model.py` — `choose_threshold()` and `evaluate()`.
3. `src/pipeline/registry.py` — `decision()`, `promote()`, `rollback()`.
4. `src/pipeline/drift.py` — PSI, bands, and the note in the report.
5. `cli.py` — how a stage becomes an exit code.
6. `.github/workflows/quality.yml` — the same commands, in CI order.

---

## Exercises

1. **Measure the leak.** Replace `split_by_machine` with a random 80/20 row split,
   train, and record ROC AUC. Then restore the group split. Explain the
   difference in one paragraph without using the word "overfit".
2. **Move the threshold.** Set `target_recall: 0.5` and rerun. Record recall,
   precision, and false positives. Which policy gate now fails, and is that the
   right gate to relax?
3. **Break the gate.** Edit `artifacts/run_meta.json` to claim `roc_auc: 0.99`,
   run `promote`, and observe that it passes. Then explain why a registry must
   recompute metrics from the artifact rather than trust a JSON file written by
   the same process. This is the most important limitation of the local registry.
4. **Add a feature-level owner.** Extend `configs/pipeline.yaml` with a mapping
   from feature to team, and include it in the drift report so an alert names who
   to call.
5. **Sample-size sensitivity.** Generate a 60-row reference and compute PSI
   against the same batch. How much does the value move? What does that imply for
   choosing a threshold on small windows?
6. **Retraining decision memo.** Write 200 words recommending or refusing a
   retrain, naming the evidence you have, the evidence you lack, and the cost of
   each choice.

---

## Common problems

| Symptom | Cause | Fix |
|---|---|---|
| `DataError: ... run python make_data.py first` | No generated data | `python make_data.py` |
| `single class after holding out ...` | Too few machines or positives | Use more rows (`--rows 800`) or fewer holdouts |
| `monitor` exits 2 and your CI marks the build red | Drift treated as failure | Separate the step and record the report, as the workflow does |
| PSI differs slightly between machines | Bins come from reference quantiles; a different reference changes them | Compare with the same reference file and record its hash |
| `promote` blocked | Policy not met | Read the printed reasons; do not lower a gate without writing down why |
| `rollback` says "nothing to roll back to" | Only one version registered | Register a second version first |

---

## Cleanup

```bash
rm -rf data artifacts .pytest_cache .venv
```

```powershell
Remove-Item data, artifacts, .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue
```

---

## Where this sits in the course

| Before this | This starter | Next |
|---|---|---|
| [Intermediate starter](../intermediate-eta-service/README.md) | A gated, monitored lifecycle | [Capstone](../../../docs/projects/capstone.md) |
| [Module 09 · Registry](../../../docs/modules/09-model-registry/index.md) | The policy idea, with a real registry | [Module 14 · Monitoring](../../../docs/modules/14-monitoring-drift/index.md) |
| [Lab 17 · Drift analysis](../../../docs/labs/lab-17-drift-analysis.md) | A guided drift diagnosis | [MP4 · Monitored lifecycle](../../../docs/projects/mini-projects/mp-04-monitored-lifecycle.md) |

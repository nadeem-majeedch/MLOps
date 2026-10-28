# Concepts · Module 04

## 1. A data contract is a promise with a test

A **data contract** is an agreement between the team that produces data and the team that consumes it, about what the data will look like. A **schema** is the machine-checkable part of that contract: column names, types, nullability, ranges, allowed values.

Contracts fail in three ways, and each needs a different check:

| Failure | Example | Check type |
|---|---|---|
| Shape changed | A column renamed `pickup_ts` → `requested_at` | Column presence and type |
| Values changed | Distances recorded in miles | Range plus a cross-field rule |
| Meaning changed | A zone code reused for a different area | Domain set, owned by a person |

Only the first is caught by most schema libraries by default. The third is caught by nothing except a human who owns the vocabulary, which is why a data contract has an owner.

## 2. Eight kinds of check, and what each catches

The RaviRide dataset gets eight checks. They are deliberately small and hand-written: declarative libraries are excellent, but you cannot debug a check you cannot read.

| # | Check | Catches | Example failure |
|---|---|---|---|
| 1 | Required columns | Renamed or dropped column | Upstream renamed `requested_at` |
| 2 | Identifier uniqueness | Duplicate deliveries, retries | Same trip delivered twice |
| 3 | Distance range | Negative values, unit mix-ups | `-3.68` km |
| 4 | Duration range | Placeholder sentinels like `-1` or `9999` | A cancelled trip coded `0` |
| 5 | Zone domain | Retired or new zone codes | `Z99` after a boundary change |
| 6 | Passenger and supply ranges | Impossible counts | `0` passengers, `120` drivers |
| 7 | Timestamp window | Time-zone shifts, bad parsing, future data | A row dated next year |
| 8 | Implied speed | Unit confusion, swapped columns | 40 km in 5 minutes |

Check 8 is the interesting one: it is **cross-field**, combining two columns to test a physical plausibility rule. Cross-field checks catch the errors that per-column checks cannot, because each column individually looks fine.

### What a good failure message contains

Three things, every time: how many rows failed, which rule failed, and one example row the reader can open.

```text
FAIL data/raw/trips_bad.csv: 1200 rows, 3 check(s) failed
  - trip_id_unique: 6 rows share an id, e.g. T000704 (row 0)
  - distance_km_range: 5 rows outside 0-60 km, e.g. T000053 (row 52) has -3.68
  - pickup_zone_known: 4 rows with unknown zone, e.g. T000316 (row 315) has Z99
```

That is real output from this module's reference implementation. "Validation failed" is not a report; it costs the reader the next hour.

## 3. Fail, don't filter

The tempting implementation is `df = df[df.distance_km > 0]`. Do not.

Dropping bad rows means the pipeline silently trains on a different dataset than the one delivered. Metrics move, nobody knows why, and the defect is never reported to the team that produced it. A failed run is cheap; a quiet change in the training population is expensive.

There are exactly two legitimate cases for filtering:

1. **The check has established the rows are outside the population of interest**, and that exclusion is declared, counted, and reported (for example, test rides with `distance_km == 0`).
2. **The pipeline is explicitly a quarantine step** that writes rejects to a file for the data owner, and fails if the reject rate exceeds a threshold.

Outliers need a third decision. A 60 km trip may be genuine; a −3 km trip is not. Numeric checks should encode physical limits, not percentiles, or every holiday will stop the pipeline.

## 4. Leakage: when the model cheats

**Leakage** is any information in the features that would not be available at prediction time, or that encodes the target. Two forms matter here.

**Target leakage.** A column computed from the outcome. In this dataset, `fare_amount` is calculated by the meter after the trip, partly from its duration:

```python
corr(fare_amount, duration_min) = 0.997
```

A model given `fare_amount` reports an MAE of **0.66 minutes** on a random holdout, against **5.40 minutes** for the same model without it. The impressive number is not a better model; it is the answer, restated. At booking time the fare does not exist, so the model cannot run at all.

**Temporal leakage.** Using future information to predict the past. Sorting the data by request time and splitting randomly puts September's rainy trips in both train and test. The model appears to handle rain, because it has seen the same rainy days. A temporal split - train on everything before 22 September, test on the last week - tells the truth:

```text
train: 896 rows 2026-09-01 02:56 .. 2026-09-21 23:36
test:  304 rows 2026-09-22 02:04 .. 2026-09-28 23:23
```

Both numbers above are measured on the course dataset. The lesson is not that the leaky model is inaccurate; it is that its accuracy is unmeasurable by the same procedure that produced it.

### Finding leakage systematically

Three cheap heuristics:

1. **Ask of each feature: could I know this at the moment of prediction?** If the answer needs a qualify, the feature is suspect.
2. **Correlation with the target above ~0.95** is a warning, not a proof. Inspect any such column and its provenance.
3. **Check the correlation of each feature with time.** Strong correlation with the future suggests the value is recorded later than the event.

## 5. Provenance and the dataset README

**Provenance** answers: where did this data come from, how was it produced, and what is wrong with it? For a synthetic course dataset the answers are short, but the habit must be established now, because for real data it is the difference between an auditable model and an unexplainable one.

The dataset README records:

| Field | Example |
|---|---|
| Source | Generated by `scripts/generate_trips.py`, seed 42 |
| Command | `python scripts/generate_trips.py --out data/raw/trips.csv` |
| Rows and window | 1,200 rows, 2026-09-01 to 2026-09-28 |
| Checksum | md5 `847fa5b817ba46ad0e81df2c4f273e59` |
| Licence | Course-generated synthetic data; no personal data |
| Known limitations | Eight synthetic zones; no weather from a real feed; one month only |
| Invalidates the model | A change to zone definitions, to the duration formula, or to the seed |

## 6. Why Git is not a data store

Git is a content-addressed store for text. It handles small files well and large binaries badly: every version is stored in full in the repository history, clones become slow, and a 500 MB CSV committed once is there forever.

Git also has no concept of "the data lives elsewhere". A team that commits data quickly learns to rewrite history, which is a dangerous operation on a shared branch.

## 7. DVC: the same idea, different store

**DVC** (Data Version Control) records the *identity* of a file in Git and keeps the *contents* elsewhere, in a **cache** and, optionally, a **remote**.

```powershell
dvc init
dvc add data/raw/trips.csv
```

`dvc add` moves the file into `.dvc/cache` (named by its hash), writes `data/raw/trips.csv.dvc`, and adds the data path to `.gitignore`. The `.dvc` file is small and goes into Git:

```yaml
outs:
- md5: 847fa5b817ba46ad0e81df2c4f273e59
  size: 83182
  hash: md5
  path: trips.csv
```

That is a **content address**: the file's name no longer matters, only its hash. Two consequences follow. Identical files are stored once; and any commit that points at this hash can retrieve exactly these bytes.

| Command | Effect |
|---|---|
| `dvc add <path>` | Hash the file, cache it, write the `.dvc` pointer, ignore the data |
| `dvc push` | Upload cache objects to the configured remote |
| `dvc pull` | Download the objects a `.dvc` file needs, then check them out |
| `dvc checkout` | Restore working files from the local cache |
| `dvc status` | Show what differs from the pointers |

A remote can be any storage DVC supports. For this course it is a directory on the same machine:

```powershell
mkdir C:\dvcstore
dvc remote add -d localstore C:\dvcstore
dvc push
```

Verified in the reference implementation: `7 files pushed`, and after deleting `data/raw/trips.csv`, `dvc pull` restored it with the same md5 and size.

## 8. What DVC does not do

DVC versions *files*. It does not record how a file was produced, which code read it, or which parameters were used. Those are pipeline concerns, and they are Module 05's subject (`dvc.yaml`, `dvc.lock`).

It also does not validate anything. A perfectly versioned dataset can be perfectly wrong. Version and validation are independent controls, and a mature project needs both.

## 9. Declarative validation: when to use a library

The hand-written checks above are readable and dependency-free. `pandera` expresses the same rules as data:

```python
schema = pa.DataFrameSchema({
    "distance_km": pa.Column(float, pa.Check.gt(0), nullable=False),
    "pickup_zone": pa.Column(str, pa.Check.isin(["Z01", "Z02"])),
})
schema.validate(frame, lazy=True)
```

On two bad rows this raises `SchemaErrors` with `failure cases: 2` - both faults reported at once, because `lazy=True` collects instead of stopping.

Use a library when the schema is large, shared with other teams, or needs statistical checks. Use hand-written checks when you need a specific message, a cross-field rule, or no new dependency. Most real projects end up with both: a schema for the shape, and a few deliberate functions for the rules that matter.

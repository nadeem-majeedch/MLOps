# Worked example · One check, done properly

Most validation failures are not "the check did not fire"; they are "the check fired and nobody could tell why". This example builds one check end to end, then the report around it.

## Step 1: the failing check, naively

```python
def validate(frame):
    if (frame["distance_km"] <= 0).any():
        raise ValueError("invalid distance")
```

Three problems, and every one of them will cost a colleague time:

- It says nothing about how many rows, which ones, or what value.
- It stops at the first failing rule, so a batch with three defects is fixed in three runs.
- `ValueError` is indistinguishable from a bug in the validator itself.

## Step 2: the same check with a useful message

```python
distance = pd.to_numeric(frame["distance_km"], errors="coerce")
bad = distance.isna() | (distance <= 0) | (distance > 60)
if bad.any():
    row = frame.loc[bad].iloc[0]
    report.failures.append(
        f"distance_km_range: {int(bad.sum())} rows outside 0-60 km, "
        f"e.g. {row['trip_id']} (row {frame.index[bad][0]}) has {row['distance_km']}"
    )
```

Four decisions are embedded here, and each is worth copying:

1. **`pd.to_numeric(..., errors="coerce")`**, because a CSV column can arrive as strings. Coercion turns "not a number" into `NaN`, which the check can report instead of crashing.
2. **A compound mask**, so `NaN`, negative, and absurd values are one failure, not three.
3. **A domain limit (60 km), not a percentile.** A long trip is unusual, not illegal.
4. **One example row**, chosen deterministically (the first), so two people reading the message see the same thing.

## Step 3: a report that collects instead of stopping

```python
@dataclass
class ValidationReport:
    path: str
    rows: int
    failures: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

    def render(self) -> str:
        if self.ok:
            return f"PASS {self.path}: {self.rows} rows, 8 checks"
        lines = [f"FAIL {self.path}: {self.rows} rows, {len(self.failures)} check(s) failed"]
        lines += [f"  - {failure}" for failure in self.failures]
        return "\n".join(lines)
```

Each check appends; nothing raises until the end. The caller decides the policy:

```python
report = validate_trips(frame, path="data/raw/trips.csv")
print(report.render())
report.raise_if_failed()
```

That separation matters. In a lab you want all failures at once. In a strict pipeline you want the exception. The report supports both without duplicating checks.

## Step 4: the real outputs

A good batch:

```text
PASS data/raw/trips.csv: 1200 rows, 8 checks
```

The batch with the three reported defects:

```text
FAIL data/raw/trips_bad.csv: 1200 rows, 3 check(s) failed
  - trip_id_unique: 6 rows share an id, e.g. T000704 (row 0)
  - distance_km_range: 5 rows outside 0-60 km, e.g. T000053 (row 52) has -3.68
  - pickup_zone_known: 4 rows with unknown zone, e.g. T000316 (row 315) has Z99
```

Three things a reader can do with this in ten seconds: see the scale (3 checks, 6/5/4 rows), find the rows, and decide who to call. That is the whole standard.

Note what is *not* in the output: the word "error", a stack trace, or a line number in the validator. The report is about the data.

## Step 5: the same rules declaratively

If you prefer a library, `pandera` expresses the same intent:

```python
import pandera as pa

schema = pa.DataFrameSchema({
    "distance_km": pa.Column(float, pa.Check.gt(0), nullable=False),
    "pickup_zone": pa.Column(str, pa.Check.isin(["Z01", "Z02"])),
})
schema.validate(frame, lazy=True)
```

On a frame with a negative distance and an unknown zone:

```text
SchemaErrors | failure cases: 2
```

`lazy=True` is what makes it comparable to the hand-written report: both faults are collected. The library gives you statistics, coercion, and reuse; the hand-written version gives you exact wording and cross-field rules with almost no learning curve. Choosing either is defensible. Having neither is not.

## Step 6: what the checks still cannot see

- **Semantic correctness.** A zone code that is valid but assigned to the wrong area passes every check.
- **Distribution shift.** Every individual row can be legal while the batch is not representative. Module 06's slice metrics and Module 14's drift monitoring cover that.
- **Leakage.** `fare_amount` passes all eight checks. Only a rule about *when* a column exists catches it, which is why the leakage test is separate.

Validation is a floor, not a ceiling. Say so in the data README; it prevents someone treating "all checks pass" as "the data is right".

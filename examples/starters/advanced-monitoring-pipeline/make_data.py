"""Write the equipment dataset and a later, shifted batch.

    python make_data.py

Files:

* `data/equipment.csv`    -- 480 labelled readings from eight machines
* `data/current_batch.csv`-- 160 unlabelled readings from the same machines,
  after a maintenance interval was extended. Vibration, temperature, and days
  since service are all higher.

The batch has **no label column**, because in the situation this template models
nobody knows the outcomes yet. That is why drift is evidence about inputs, not
proof that accuracy fell: the README asks you to say what would be needed to
know.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from pathlib import Path

MACHINES = [f"M{n:02d}" for n in range(1, 9)]
FEATURES = [
    "temperature_c", "vibration_mm_s", "pressure_bar",
    "operating_hours", "days_since_service",
]
TARGET = "failure_within_7d"

COLUMNS = ["reading_id", "machine_id", *FEATURES, TARGET]
BATCH_COLUMNS = ["reading_id", "machine_id", *FEATURES]


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _reading(rng: random.Random, machine: str, index: int,
             vibration_shift: float, temp_shift: float, service_shift: int) -> list[object]:
    hours = round(rng.uniform(200, 9000), 0)
    days_service = rng.randrange(0, 220) + service_shift
    temperature = round(
        rng.gauss(68, 6) + max(0.0, days_service - 120) * 0.05 + temp_shift, 1
    )
    vibration = round(
        max(0.2, rng.gauss(2.2, 0.6) + max(0.0, hours - 6000) / 4000 + vibration_shift), 2
    )
    pressure = round(rng.gauss(4.2, 0.3), 2)
    logit = (
        -2.6
        + 0.9 * (vibration - 2.5)
        + 0.35 * (temperature - 70) / 2
        + 0.010 * max(0, days_service - 150)
        + 0.0003 * max(0, hours - 6500)
    )
    return [machine, temperature, vibration, pressure, int(hours), days_service, logit]


def write_labeled(path: Path, rows: int, seed: int) -> int:
    rng = random.Random(seed)
    records = []
    for i in range(rows):
        machine = MACHINES[i % len(MACHINES)]
        values = _reading(rng, machine, i, 0.0, 0.0, 0)
        logit = values.pop()
        label = 1 if rng.random() < _sigmoid(logit) else 0
        records.append([f"R{i + 1:04d}", *values, label])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(records)
    return sum(int(row[-1]) for row in records)


def write_batch(path: Path, rows: int, seed: int) -> None:
    rng = random.Random(seed)
    records = []
    for i in range(rows):
        machine = MACHINES[i % len(MACHINES)]
        values = _reading(rng, machine, i, 0.95, 4.0, 40)
        values.pop()  # the logit; outcomes are unknown for this batch
        records.append([f"B{i + 1:04d}", *values])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(BATCH_COLUMNS)
        writer.writerows(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("data"))
    parser.add_argument("--rows", type=int, default=480)
    parser.add_argument("--batch-rows", type=int, default=160)
    parser.add_argument("--seed", type=int, default=19)
    args = parser.parse_args()

    positives = write_labeled(args.out / "equipment.csv", args.rows, args.seed)
    write_batch(args.out / "current_batch.csv", args.batch_rows, args.seed + 1)
    print(f"wrote {args.out / 'equipment.csv'}      {args.rows} rows  {positives} positive")
    print(f"wrote {args.out / 'current_batch.csv'}  {args.batch_rows} rows  unlabelled, shifted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

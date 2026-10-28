"""Write a synthetic trip table for the ETA service template.

    python make_data.py               # data/trips.csv, 360 rows
    python make_data.py --rows 720 --seed 3

The schema matches `datasets/raviride_trips.csv` in the course repository, but
this generator is standalone, so the folder can be copied and still runs. Times
are written as ISO-8601 strings with a fixed offset, never as a localised value.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

COLUMNS = [
    "trip_id", "requested_at", "pickup_zone", "dropoff_zone", "distance_km",
    "passengers", "traffic_index", "driver_supply", "weather", "duration_min",
]

ZONES = [f"Z{i:02d}" for i in range(1, 7)]
WEATHER = ["clear", "clear", "cloud", "rain"]
START = datetime(2026, 3, 2, 6, 0, 0)


def build_rows(rows: int, seed: int) -> list[list[object]]:
    rng = random.Random(seed)
    out: list[list[object]] = []
    for i in range(rows):
        when = START + timedelta(minutes=37 * i + rng.randrange(0, 20))
        pickup, dropoff = rng.sample(ZONES, 2)
        distance = round(rng.uniform(1.0, 22.0), 1)
        passengers = rng.choices([1, 2, 3, 4], weights=[0.55, 0.25, 0.15, 0.05])[0]
        traffic = round(min(1.0, max(0.0, rng.gauss(0.45, 0.2))), 2)
        supply = rng.randrange(5, 90)
        weather = WEATHER[rng.randrange(len(WEATHER))]
        peak = 1.35 if when.hour in (8, 9, 17, 18, 19) else 1.0
        rain = 1.25 if weather == "rain" else 1.0
        duration = (
            distance * 2.1 * peak * rain
            + 3.0
            + 8.0 * distance * traffic / 10
            - supply * 0.02
            + rng.gauss(0, 1.4)
        )
        out.append([
            f"T{i + 1:04d}", when.isoformat(), pickup, dropoff, distance,
            passengers, traffic, supply, weather, round(max(2.0, duration), 1),
        ])
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=360)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--out", type=Path, default=Path("data/trips.csv"))
    args = parser.parse_args()

    rows = build_rows(args.rows, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(rows)
    print(f"wrote {args.out}  {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

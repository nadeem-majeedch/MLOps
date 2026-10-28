"""Generate the RaviRide trip extract.

Deterministic: same seed and arguments produce a byte-identical file.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# Zone centres on a rough 8 x 8 km grid; Z01..Z04 are central, Z05..Z08 outer.
ZONES = {
    "Z01": (2.0, 2.0, 1.00),
    "Z02": (3.4, 1.6, 1.06),
    "Z03": (1.4, 3.5, 0.95),
    "Z04": (4.2, 3.9, 1.12),
    "Z05": (6.5, 1.2, 1.02),
    "Z06": (7.1, 5.8, 1.18),
    "Z07": (1.1, 7.2, 1.24),
    "Z08": (6.0, 7.5, 1.31),
}
ZONE_IDS = list(ZONES)
ZONE_WEIGHTS = np.array([0.22, 0.18, 0.15, 0.14, 0.10, 0.09, 0.07, 0.05])
WEATHER = ["clear", "cloud", "rain"]
WEATHER_P = [0.62, 0.25, 0.13]
PEAK_HOURS = {7, 8, 9, 17, 18, 19}
DURATION_SIGMA = 0.2218  # multiplicative; long trips have larger absolute error
INCIDENT_SHARE = 0.005  # severe delays: road closure, breakdown, accident


def _traffic(hour: int, weekday: int, weather: str, rng: np.random.Generator) -> float:
    base = 0.22
    if hour in PEAK_HOURS:
        base += 0.34
    elif 10 <= hour <= 15:
        base += 0.08
    elif hour >= 22 or hour <= 5:
        base -= 0.10
    if weekday >= 5:
        base -= 0.06
    base += {"clear": 0.0, "cloud": 0.03, "rain": 0.09}[weather]
    return float(np.clip(base + rng.normal(0, 0.05), 0.05, 0.98))


def generate(rows: int, seed: int, duration_sigma: float = DURATION_SIGMA,
             incident_share: float = INCIDENT_SHARE, zone_weights=None,
             traffic_delta: float = 0.0, weather_p=None,
             distance_scale: float = 1.0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    start = pd.Timestamp("2026-09-01 00:00:00")
    minutes = rng.integers(0, 28 * 24 * 60, size=rows)
    requested_at = start + pd.to_timedelta(minutes, unit="m")

    weights = np.asarray(zone_weights, dtype=float) if zone_weights is not None else ZONE_WEIGHTS
    weights = weights / weights.sum()
    pickup = rng.choice(ZONE_IDS, size=rows, p=weights)
    dropoff = rng.choice(ZONE_IDS, size=rows, p=weights)
    same = pickup == dropoff
    while same.any():  # a trip has two distinct ends
        dropoff[same] = rng.choice(ZONE_IDS, size=int(same.sum()), p=ZONE_WEIGHTS)
        same = pickup == dropoff

    weather = rng.choice(WEATHER, size=rows, p=(weather_p if weather_p is not None else WEATHER_P))
    passengers = rng.choice([1, 2, 3, 4, 5, 6], size=rows, p=[0.46, 0.26, 0.13, 0.08, 0.04, 0.03])

    hour = requested_at.hour.to_numpy()
    weekday = requested_at.dayofweek.to_numpy()
    traffic = np.array([_traffic(int(h), int(d), str(w), rng) for h, d, w in zip(hour, weekday, weather, strict=False)])
    supply = np.clip(96 - 70 * traffic + rng.normal(0, 6, rows), 4, 100)

    coords = np.array([[ZONES[z][0], ZONES[z][1]] for z in ZONE_IDS])
    index = {z: i for i, z in enumerate(ZONE_IDS)}
    p_idx = np.array([index[z] for z in pickup])
    d_idx = np.array([index[z] for z in dropoff])
    manhattan = np.abs(coords[p_idx, 0] - coords[d_idx, 0]) + np.abs(coords[p_idx, 1] - coords[d_idx, 1])
    distance = np.clip(manhattan * 1.12 * distance_scale + rng.normal(0, 0.6, rows), 0.6, 45.0)

    pace = np.array([ZONES[z][2] for z in pickup])  # outer pickups are slower to reach
    weather_factor = np.array([{"clear": 1.0, "cloud": 1.04, "rain": 1.18}[w] for w in weather])
    peak_factor = np.where(np.isin(hour, list(PEAK_HOURS)), 1.16, 1.0)
    speed = 27.0 / (pace * weather_factor * (0.55 + 0.75 * traffic) * peak_factor)
    duration = distance / speed * 60 + 0.4 * passengers
    duration = duration * np.exp(rng.normal(0, duration_sigma, rows))
    incident = rng.random(rows) < incident_share
    duration = duration + np.where(incident, rng.uniform(35, 70, rows), 0.0)
    # Keep the draw physically plausible: the validation rules allow 3..120 km/h.
    duration = np.clip(duration, distance / 108 * 60, distance / 3.6 * 60)
    duration = np.clip(duration, 1.0, 240.0)

    fare = 2.20 + 0.78 * distance + 0.34 * duration + rng.normal(0, 0.35, rows)

    frame = pd.DataFrame(
        {
            "trip_id": [f"T{i:06d}" for i in range(1, rows + 1)],
            "requested_at": requested_at,
            "pickup_zone": pickup,
            "dropoff_zone": dropoff,
            "distance_km": np.round(distance, 2),
            "duration_min": np.round(duration, 1),
            "passengers": passengers,
            "driver_supply": np.round(supply).astype(int),
            "traffic_index": np.round(traffic, 3),
            "weather": weather,
            "fare_amount": np.round(fare, 2),
        }
    )
    return frame.sort_values("requested_at").reset_index(drop=True)


def corrupt(frame: pd.DataFrame, seed: int = 7) -> pd.DataFrame:
    """Plant three defects: negative distances, duplicate ids, a retired zone."""
    rng = np.random.default_rng(seed)
    bad = frame.copy()

    negative = rng.choice(bad.index, size=6, replace=False)
    bad.loc[negative, "distance_km"] = -bad.loc[negative, "distance_km"]

    duplicated = rng.choice(bad.index, size=5, replace=False)
    donors = rng.choice([i for i in bad.index if i not in set(duplicated)], size=5, replace=False)
    bad.loc[duplicated, "trip_id"] = bad.loc[donors, "trip_id"].to_numpy()

    retired = rng.choice(bad.index, size=4, replace=False)
    bad.loc[retired, "pickup_zone"] = "Z99"
    return bad


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--rows", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--corrupt", action="store_true")
    args = parser.parse_args()

    frame = generate(args.rows, args.seed)
    if args.corrupt:
        frame = corrupt(frame)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False, date_format="%Y-%m-%d %H:%M:%S")
    print(f"wrote {len(frame)} rows -> {out}")


if __name__ == "__main__":
    main()

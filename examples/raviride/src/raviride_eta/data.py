"""Loading and validation. Returns a report; never raises on the first defect."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "trip_id", "requested_at", "pickup_zone", "dropoff_zone", "distance_km",
    "duration_min", "passengers", "driver_supply", "traffic_index", "weather",
    "fare_amount",
]
KNOWN_ZONES = {f"Z{i:02d}" for i in range(1, 9)}


class DataValidationError(RuntimeError):
    """Raised when a batch fails validation."""


@dataclass
class ValidationReport:
    path: str
    rows: int = 0
    checks: int = 8
    failures: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

    def render(self) -> str:
        head = f"{'PASS' if self.ok else 'FAIL'} {self.path}: {self.rows} rows, {self.checks} checks"
        if self.ok:
            return head
        return head + "\n" + "\n".join(f"  - {f}" for f in self.failures)

    def raise_if_failed(self) -> None:
        if not self.ok:
            raise DataValidationError(self.render())


def _example(frame: pd.DataFrame, mask: pd.Series) -> str:
    row = frame[mask].index[0]
    trip = frame.loc[row, "trip_id"]
    return f"{trip} (row {row})"


def validate_trips(frame: pd.DataFrame, path: str, window: tuple[str, str], checks: int = 8) -> ValidationReport:
    report = ValidationReport(path=path, rows=len(frame), checks=checks)
    missing = [c for c in EXPECTED_COLUMNS if c not in frame.columns]
    if missing:
        report.failures.append(f"required_columns: missing {missing}")
        return report

    dup = frame["trip_id"].duplicated()
    if dup.any():
        report.failures.append(f"trip_id_unique: {int(dup.sum())} duplicated ids, first {_example(frame, dup)}")

    bad = ~frame["distance_km"].between(0, 60, inclusive="right")
    if bad.any():
        report.failures.append(
            f"distance_km_range: {int(bad.sum())} rows outside (0, 60], first {_example(frame, bad)}"
        )

    bad = ~frame["duration_min"].between(1, 240)
    if bad.any():
        report.failures.append(
            f"duration_min_range: {int(bad.sum())} rows outside [1, 240], first {_example(frame, bad)}"
        )

    for column in ("pickup_zone", "dropoff_zone"):
        bad = ~frame[column].isin(KNOWN_ZONES)
        if bad.any():
            unknown = sorted(frame.loc[bad, column].unique())
            report.failures.append(
                f"{column}_known: {int(bad.sum())} rows with unknown zones {unknown}, "
                f"first {_example(frame, bad)}"
            )

    bad = ~frame["passengers"].between(1, 6) | ~frame["driver_supply"].between(1, 100)
    if bad.any():
        report.failures.append(
            f"counts_range: {int(bad.sum())} rows outside passenger/supply bounds, "
            f"first {_example(frame, bad)}"
        )

    requested = pd.to_datetime(frame["requested_at"], errors="coerce")
    start, end = pd.Timestamp(window[0]), pd.Timestamp(window[1]) + timedelta(days=1)
    bad = requested.isna() | (requested < start) | (requested >= end)
    if bad.any():
        report.failures.append(
            f"requested_at_window: {int(bad.sum())} rows unparsable or outside "
            f"{window[0]}..{window[1]}, first {_example(frame, bad)}"
        )

    usable = frame["distance_km"].gt(0) & frame["duration_min"].gt(0)
    hours = frame["duration_min"].where(usable) / 60
    speed = frame["distance_km"].where(usable) / hours
    bad = usable & ~speed.between(3, 120)
    if bad.any():
        report.failures.append(
            f"implied_speed: {int(bad.sum())} rows outside 3..120 km/h, first {_example(frame, bad)}"
        )

    return report


def load_trips(path: Path, window: tuple[str, str]) -> tuple[pd.DataFrame, ValidationReport]:
    frame = pd.read_csv(path, parse_dates=["requested_at"])
    report = validate_trips(frame, str(path), window)
    return frame, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    import yaml

    from .config import PARAMS_PATH

    params = yaml.safe_load(open(PARAMS_PATH, encoding="utf-8"))
    frame = pd.read_csv(args.path, parse_dates=["requested_at"])
    window = (params["data"]["window_start"], params["data"]["window_end"])
    report = validate_trips(frame, args.path, window)
    print(report.render())
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())

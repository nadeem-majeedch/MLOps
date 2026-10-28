"""Stage 1: validate the raw extract, then split it by time."""

from __future__ import annotations

from datetime import timedelta

from .config import load_params, project_path
from .data import load_trips


def main() -> int:
    params = load_params()
    window = (params["data"]["window_start"], params["data"]["window_end"])
    frame, report = load_trips(project_path("data", "raw", "trips.csv"), window)
    print(report.render())
    report.raise_if_failed()

    frame = frame.sort_values("requested_at").reset_index(drop=True)
    held_out_days = int(params["data"]["test_days"])
    cutoff = frame["requested_at"].max().floor("D") - timedelta(days=held_out_days - 1)
    train = frame[frame["requested_at"] < cutoff]
    test = frame[frame["requested_at"] >= cutoff]

    processed = project_path("data", "processed")
    processed.mkdir(parents=True, exist_ok=True)
    train.to_csv(processed / "train.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    test.to_csv(processed / "test.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    print(f"train: {len(train)} rows {train['requested_at'].min()} .. {train['requested_at'].max()}")
    print(f"test:  {len(test)} rows {test['requested_at'].min()} .. {test['requested_at'].max()}")
    print(f"cutoff: {cutoff}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Write fourteen days of prediction logs, with one release in the middle.

    python make_logs.py

Each line is one served request with the delayed label attached. The service
changed version on 2026-10-11, which is the only structural change in the file.
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from make_sessions import make  # noqa: E402

START = date(2026, 10, 4)
DAYS = 14
SWITCH = date(2026, 10, 11)


def main() -> None:
    rng = np.random.default_rng(77)
    out = Path("data/predictions.jsonl")
    out.parent.mkdir(exist_ok=True)

    rows = []
    request = 1
    for offset in range(DAYS):
        day = START + timedelta(days=offset)
        frame = make(rows=140, seed=300 + offset)
        # One session in five is a long one. The generator rarely produces
        # hours above 6 on its own, and that slice is the point of the lab.
        long_sessions = rng.random(len(frame)) < 0.20
        frame.loc[long_sessions, "hours"] = np.round(rng.uniform(6.2, 10.0, int(long_sessions.sum())), 2)
        for _, record in frame.iterrows():
            hours = float(record["hours"])
            truth = float(np.clip(
                18 + 4.9 * hours + 0.66 * record["prior_score"] + 2.1 * (record["sleep_hours"] - 6.8)
                + rng.normal(0, 4.5), 0, 100))
            if day < SWITCH:
                version, bias, sigma = "v3", 0.0, 3.4
            else:
                version = "v4"
                bias, sigma = (7.0, 4.2) if hours > 6 else (-0.3, 3.2)
            prediction = truth - bias + rng.normal(0, sigma)
            rows.append(
                {
                    "request_id": f"r{request:06d}",
                    "when": f"{day.isoformat()}T{int(rng.integers(7, 22)):02d}:{int(rng.integers(0, 60)):02d}:00",
                    "version": version,
                    "hours": round(hours, 2),
                    "prior_score": round(float(record["prior_score"]), 1),
                    "sleep_hours": round(float(record["sleep_hours"]), 1),
                    "prediction": round(float(np.clip(prediction, 0, 100)), 2),
                    "actual": round(truth, 1),
                }
            )
            request += 1

    with out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    print(f"wrote {len(rows)} predictions across {DAYS} days -> {out}")
    print(f"version change on {SWITCH.isoformat()}")


if __name__ == "__main__":
    main()

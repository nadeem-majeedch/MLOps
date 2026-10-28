"""Write a small synthetic student-support dataset for this template.

    python make_data.py            # data/study_support.csv, 300 rows
    python make_data.py --rows 600 --seed 11

This template is self-contained: it does not import the course dataset
generator, so you can copy the folder anywhere and it still runs. The schema
matches `datasets/study_support.csv`; the seed and row count do not, so the
numbers here will differ from the lab pages. That is expected.

No real student record is used or represented. `student_ref` is a sequence
number.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from pathlib import Path

COLUMNS = [
    "student_ref", "term", "prior_gpa_band", "attendance_rate",
    "lms_logins_week", "assignments_submitted", "support_contacts",
    "needs_support",
]


def build_rows(rows: int, seed: int) -> list[list[object]]:
    rng = random.Random(seed)
    out: list[list[object]] = []
    for i in range(rows):
        band = rng.choices(["low", "mid", "high"], weights=[0.25, 0.5, 0.25])[0]
        attendance = min(1.0, max(0.35, rng.gauss(
            {"low": 0.62, "mid": 0.78, "high": 0.9}[band], 0.1)))
        logins = max(0.0, rng.gauss({"low": 3.0, "mid": 7.0, "high": 11.0}[band], 2.5))
        submitted = min(12, max(0, round(rng.gauss(
            {"low": 6, "mid": 9, "high": 11}[band], 2))))
        contacts = rng.choices([0, 1, 2, 3], weights=[0.5, 0.3, 0.15, 0.05])[0]
        term = ["2025-Fall", "2026-Spring"][i % 2]
        logit = (
            -1.1
            + 4.2 * (0.6 - attendance)
            + 0.22 * (6 - logins)
            + 0.30 * (8 - submitted)
            + 0.35 * contacts
            + (0.5 if band == "low" else -0.2 if band == "high" else 0.0)
            + (0.25 if term == "2026-Spring" else 0.0)
        )
        risk = 1 if rng.random() < 1 / (1 + math.exp(-logit)) else 0
        out.append([
            f"S{i + 1:04d}", term, band, round(attendance, 3), round(logins, 1),
            submitted, contacts, risk,
        ])
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=300)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=Path, default=Path("data/study_support.csv"))
    args = parser.parse_args()

    rows = build_rows(args.rows, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(rows)
    positives = sum(int(row[-1]) for row in rows)
    print(f"wrote {args.out}  {len(rows)} rows  {positives} positive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

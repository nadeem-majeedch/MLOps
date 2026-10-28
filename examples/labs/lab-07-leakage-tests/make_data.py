"""Build the dataset for Lab 07: sessions grouped by student.

    python make_data.py

300 sessions from 90 students. Some students appear three or four times, which
is what makes a row-wise split dishonest: the model can memorise a student in
training and meet the same student again in the test set.

`score_band` is written by the reporting job after the score is known. It is a
convenient feature and a direct view of the target.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

STUDENTS = 90
SEED = 23


def main() -> None:
    rng = np.random.default_rng(SEED)
    rows = []
    for index in range(1, STUDENTS + 1):
        ability = float(np.clip(rng.normal(62, 11), 25, 96))
        sleep_habit = float(np.clip(rng.normal(6.8, 1.0), 4, 9.5))
        for session in range(int(rng.integers(2, 6))):
            hours = float(np.clip(np.round(rng.gamma(2.4, 0.85), 2), 0.25, 12))
            prior = float(np.clip(ability + rng.normal(0, 4), 0, 100))
            if rng.random() < 0.04:
                prior = np.nan  # the form was not submitted
            sleep = float(np.clip(sleep_habit + rng.normal(0, 0.6), 3.5, 10))
            score = 18 + 4.9 * hours + 0.66 * (ability if np.isnan(prior) else prior) + 2.1 * (sleep - 6.8)
            score = float(np.clip(score + rng.normal(0, 5.2), 0, 100))
            rows.append(
                {
                    "student_id": f"ST{index:03d}",
                    "session_id": f"ST{index:03d}-{session + 1}",
                    "section": str(rng.choice(["A", "B", "C"])),
                    "hours": hours,
                    "prior_score": round(prior, 1) if not np.isnan(prior) else np.nan,
                    "sleep_hours": round(sleep, 1),
                    "score": round(score, 1),
                }
            )

    frame = pd.DataFrame(rows)
    frame["score_band"] = pd.cut(frame["score"], [0, 60, 75, 101], labels=[0, 1, 2]).astype("Int64")
    out = Path("data")
    out.mkdir(exist_ok=True)
    frame.to_csv(out / "students.csv", index=False)
    print(f"wrote {len(frame)} sessions from {frame['student_id'].nunique()} students -> {out / 'students.csv'}")
    print(f"students with more than one session: {(frame['student_id'].value_counts() > 1).sum()}")
    print(f"missing prior scores: {int(frame['prior_score'].isna().sum())}")


if __name__ == "__main__":
    main()

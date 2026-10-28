"""Build four weekly batches whose truth is known.

    python make_batches.py

    week0  reference: the week the champion was trained on
    week1  more study hours per session, same relationship to the score
    week2  identical inputs, scores seven points higher (the assessment changed)
    week3  a fresh sample from the reference distribution

Two of these are interesting in different ways. One has drift and no accuracy
loss; one has accuracy loss and no drift. A monitor that conflates them will
either retrain for nothing or miss a real regression.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from make_sessions import make  # noqa: E402

OUT = Path("data/batches")


def batch(seed: int, hours_scale: float = 1.0, score_offset: float = 0.0, rows: int = 220) -> pd.DataFrame:
    frame = make(rows=rows, seed=seed)
    rng = np.random.default_rng(seed + 1000)
    frame["hours"] = np.clip(np.round(frame["hours"] * hours_scale, 2), 0.25, 16.0)
    noise = rng.normal(0, 4.5, len(frame))
    score = 24 + 5.1 * frame["hours"] + 0.62 * frame["prior_score"] + 2.3 * (frame["sleep_hours"] - 6.9) + noise
    frame["score"] = np.clip(score + score_offset, 0, 100).round(1)
    return frame


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    weeks = {
        "week0": batch(101),
        "week1": batch(102, hours_scale=1.4),
        "week2": batch(101, score_offset=7.0),
        "week3": batch(104),
    }
    for name, frame in weeks.items():
        frame.to_csv(OUT / f"{name}.csv", index=False)
        print(f"{name}: {len(frame)} rows, mean hours {frame['hours'].mean():.2f}, "
              f"mean score {frame['score'].mean():.2f}")


if __name__ == "__main__":
    main()

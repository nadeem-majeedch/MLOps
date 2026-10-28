"""Generate the small session table used by Labs 01 and 07.

Deliberately simple: 480 rows, one row per study session, with a `score`
column that is a function of `hours` and `prior_score`. Everything is
synthetic; no student data is involved.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SECTION = ["A", "B", "C"]


def make(rows: int = 480, seed: int = 11) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # Sessions are logged in quarter hours; nothing shorter than 15 minutes is
    # a real session, so the generator does not pretend to produce one.
    hours = np.clip(np.round(rng.gamma(2.2, 0.9, rows), 2), 0.25, 16.0)
    prior = np.clip(rng.normal(61, 12, rows), 20, 98).round(1)
    sleep = np.clip(rng.normal(6.9, 1.0, rows), 3.5, 9.5).round(1)
    section = rng.choice(SECTION, rows)
    # The "post-test" score is what the model must predict.
    score = 24 + 5.1 * hours + 0.62 * prior + 2.3 * (sleep - 6.9) + rng.normal(0, 5.0, rows)
    score = np.clip(score, 0, 100).round(1)
    return pd.DataFrame(
        {
            "session_id": [f"S{i:04d}" for i in range(1, rows + 1)],
            "section": section,
            "hours": hours,
            "prior_score": prior,
            "sleep_hours": sleep,
            "score": score,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/sessions.csv")
    parser.add_argument("--rows", type=int, default=480)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()
    frame = make(args.rows, args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False)
    print(f"wrote {len(frame)} rows -> {out}")


if __name__ == "__main__":
    main()

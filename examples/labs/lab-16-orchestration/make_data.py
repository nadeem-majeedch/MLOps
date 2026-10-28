"""Sessions with a date column, one month, enough rows per day to train.

    python make_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from make_sessions import make  # noqa: E402

DAYS = pd.date_range("2026-09-01", "2026-09-30", freq="D")


def main() -> None:
    rng = np.random.default_rng(5)
    frame = make(rows=1800, seed=11)
    frame["session_date"] = rng.choice(DAYS, size=len(frame))
    frame = frame.sort_values(["session_date", "session_id"]).reset_index(drop=True)

    out = Path("data")
    out.mkdir(exist_ok=True)
    frame.to_csv(out / "sessions.csv", index=False, date_format="%Y-%m-%d")
    counts = frame.groupby(frame["session_date"].dt.strftime("%Y-%m-%d")).size()
    print(f"wrote {len(frame)} rows across {counts.size} days -> {out / 'sessions.csv'}")
    print(f"smallest day: {counts.min()} rows, largest: {counts.max()} rows")


if __name__ == "__main__":
    main()

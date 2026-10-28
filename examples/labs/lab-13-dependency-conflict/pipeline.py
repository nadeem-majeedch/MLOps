"""Lab 13 starter: code written against pandas 1.5, run on pandas 2.2.

    python pipeline.py

The failure is not a missing package. Both versions install. The code calls an
API the newer version removed, and nothing in the environment says so until the
line runs.

Two jobs:

1. Make this pipeline run on the pinned environment without downgrading it.
2. Make the conflict impossible to reintroduce silently: a unified requirements
   file that installs, and a test that fails if the API contract changes.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA = Path("data/sessions.csv")
EXTRA = Path("data/extra_sessions.csv")
OUT = Path("artifacts/summary.json")


def load() -> pd.DataFrame:
    frame = pd.read_csv(DATA)
    extra = pd.read_csv(EXTRA)
    # Removed in pandas 2.0. Kept here because the legacy service used it.
    return frame.append(extra, ignore_index=True)


def summarise(frame: pd.DataFrame) -> dict:
    return {
        "rows": int(len(frame)),
        "mean_hours": round(float(frame["hours"].mean()), 3),
        "mean_score": round(float(frame["score"].mean()), 3),
        "sections": sorted(frame["section"].unique().tolist()),
    }


def main() -> int:
    summary = summarise(load())
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(pd.Series(summary).to_json(indent=2) + "\n", encoding="utf-8")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

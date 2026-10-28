"""Reference solution for Lab 13: the pandas 2 way, with the intent preserved."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA = Path("data/sessions.csv")
EXTRA = Path("data/extra_sessions.csv")
OUT = Path("artifacts/summary.json")


def load() -> pd.DataFrame:
    frame = pd.read_csv(DATA)
    extra = pd.read_csv(EXTRA)
    # DataFrame.append was removed in pandas 2.0. concat is the replacement and
    # makes the axis explicit, which the old call hid.
    combined = pd.concat([frame, extra], ignore_index=True, axis=0)
    return combined.drop_duplicates(subset="session_id").reset_index(drop=True)


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

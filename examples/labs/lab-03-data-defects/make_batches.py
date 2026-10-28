"""Build the three weekly drops used in Lab 03.

    python make_batches.py

Writes:
    data/clean_batch.csv        the Tuesday drop, 180 rows, no defects
    data/bad_batch.csv          the Wednesday drop, four defect groups planted
    data/schema_change.csv      the Thursday drop, produced by a renamed column

The defects are deterministic. The counts are stated in the lab sheet, so you
can tell "found something" from "found all of it".
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from make_sessions import make  # noqa: E402

OUT = Path("data")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    clean = make(rows=180, seed=11)
    clean.to_csv(OUT / "clean_batch.csv", index=False)
    print(f"clean_batch.csv      {len(clean)} rows")

    bad = clean.copy()
    # 6 missing sleep values
    bad.loc[[5, 17, 33, 48, 101, 144], "sleep_hours"] = float("nan")
    # 3 impossible study durations
    bad.loc[[7, 61, 120], "hours"] = [31.2, 27.5, 40.0]
    # 4 duplicated identifiers (the ids of rows 10..13 copied onto rows 90..93)
    bad.loc[[90, 91, 92, 93], "session_id"] = bad.loc[[10, 11, 12, 13], "session_id"].to_numpy()
    # 2 sessions logged against a section that does not exist
    bad.loc[[22, 130], "section"] = "D"
    bad.to_csv(OUT / "bad_batch.csv", index=False)
    print(f"bad_batch.csv        {len(bad)} rows, 4 defect groups")

    renamed = clean.rename(columns={"prior_score": "prior_grade"})
    renamed["cohort"] = "2026-autumn"
    renamed.to_csv(OUT / "schema_change.csv", index=False)
    print(f"schema_change.csv    {len(renamed)} rows, 1 renamed and 1 extra column")


if __name__ == "__main__":
    main()

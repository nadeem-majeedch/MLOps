"""Stage 2: materialise features for both splits."""

from __future__ import annotations

import pandas as pd

from .config import project_path
from .features import add_features


def _one(name: str) -> None:
    source = project_path("data", "processed", f"{name}.csv")
    frame = pd.read_csv(source, parse_dates=["requested_at"])
    before = set(frame.columns)
    out = add_features(frame)
    added = [c for c in out.columns if c not in before]
    out.to_csv(project_path("data", "features", f"{name}.csv"), index=False, date_format="%Y-%m-%d %H:%M:%S")
    print(f"{name}: {len(out)} rows, added {added} -> {name}.csv")


def main() -> int:
    project_path("data", "features").mkdir(parents=True, exist_ok=True)
    for split in ("train", "test"):
        _one(split)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

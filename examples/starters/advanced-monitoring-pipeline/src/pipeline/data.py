"""Schema checks and a group-aware split.

Two ideas this module exists to teach:

1. Validation is a **contract**, not a formality. Each rule returns an error that
   names the column and the rule, because "something went wrong" costs an hour.
2. Splitting by machine is not a refinement. A random split puts the same
   machine's readings on both sides, and the model learns the machine rather than
   the physics. The difference is visible in the reference solution's metrics.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

GROUP = "machine_id"
TARGET = "failure_within_7d"
FEATURES = [
    "temperature_c", "vibration_mm_s", "pressure_bar",
    "operating_hours", "days_since_service",
]

RANGES = {
    "temperature_c": (30.0, 110.0),
    "vibration_mm_s": (0.0, 8.0),
    "pressure_bar": (2.0, 6.5),
    "operating_hours": (0, 20000),
    "days_since_service": (0, 400),
}


class DataError(ValueError):
    """The table cannot be used, and the message says which rule failed."""


def load(path: str | Path, require_target: bool = True) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise DataError(f"{path} does not exist; run `python make_data.py` first")
    frame = pd.read_csv(path)
    validate(frame, require_target=require_target)
    return frame


def validate(frame: pd.DataFrame, require_target: bool = True) -> None:
    if frame.empty:
        raise DataError("the table has no rows")

    needed = [GROUP, *FEATURES] + ([TARGET] if require_target else [])
    missing = [c for c in needed if c not in frame.columns]
    if missing:
        raise DataError(f"missing columns: {missing}")

    if "reading_id" in frame.columns and frame["reading_id"].duplicated().any():
        count = int(frame["reading_id"].duplicated().sum())
        raise DataError(f"{count} duplicate reading_id value(s)")

    nulls = frame[[GROUP, *FEATURES]].isna().sum()
    if nulls.any():
        raise DataError(f"null values: {nulls[nulls > 0].to_dict()}")

    for column, (low, high) in RANGES.items():
        outside = ~frame[column].between(low, high)
        if outside.any():
            examples = frame.loc[outside, column].head(3).tolist()
            raise DataError(
                f"{column}: {int(outside.sum())} value(s) outside [{low}, {high}], e.g. {examples}"
            )

    if frame[GROUP].nunique() < 3:
        raise DataError(f"{GROUP} has {frame[GROUP].nunique()} distinct values; at least 3 are needed to split by group")

    if require_target:
        if not frame[TARGET].isin([0, 1]).all():
            raise DataError(f"{TARGET} must contain only 0 and 1")
        if frame[TARGET].nunique() < 2:
            raise DataError(f"{TARGET} has a single class; nothing to learn or measure")


def split_by_machine(
    frame: pd.DataFrame, holdout_machines: int = 2
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Hold out whole machines, deterministically, and check both sides have signal."""
    machines = sorted(frame[GROUP].unique())
    if holdout_machines >= len(machines):
        raise DataError(f"cannot hold out {holdout_machines} of {len(machines)} machines")
    holdout = machines[-holdout_machines:]
    train = frame[~frame[GROUP].isin(holdout)].reset_index(drop=True)
    test = frame[frame[GROUP].isin(holdout)].reset_index(drop=True)

    for name, part in (("train", train), ("test", test)):
        if part[TARGET].nunique() < 2:
            raise DataError(
                f"the {name} side has a single class after holding out {holdout}; "
                "add data or choose different machines"
            )
    return train, test

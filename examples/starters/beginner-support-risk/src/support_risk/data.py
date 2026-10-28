"""Load, validate, and split the support-risk table.

The rules are deliberately explicit rather than inferred. A beginner project's
most common silent failure is a column that quietly became a string, or a target
that leaked into the features, and both are cheap to catch here.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

TARGET = "needs_support"
ID_COLUMN = "student_ref"

COLUMNS = [
    "student_ref", "term", "prior_gpa_band", "attendance_rate",
    "lms_logins_week", "assignments_submitted", "support_contacts", TARGET,
]

CATEGORICAL = ["term", "prior_gpa_band"]
NUMERIC = [
    "attendance_rate", "lms_logins_week", "assignments_submitted", "support_contacts",
]

BANDS = {"low", "mid", "high"}
TERMS = {"2025-Fall", "2026-Spring"}


class DataError(ValueError):
    """The table cannot be used for training, and the message says why."""


def load_frame(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise DataError(f"{path} does not exist; run `python make_data.py` first")
    frame = pd.read_csv(path)
    validate(frame)
    return frame


def validate(frame: pd.DataFrame) -> None:
    """Raise DataError on the first structural problem, with a specific message."""
    missing = [c for c in COLUMNS if c not in frame.columns]
    if missing:
        raise DataError(f"missing columns: {missing}")
    extra = [c for c in frame.columns if c not in COLUMNS]
    if extra:
        raise DataError(f"unexpected columns: {extra}")

    if frame.empty:
        raise DataError("the table has no rows")
    if frame[ID_COLUMN].duplicated().any():
        duplicates = int(frame[ID_COLUMN].duplicated().sum())
        raise DataError(f"{duplicates} duplicate {ID_COLUMN} value(s)")

    unknown_bands = sorted(set(frame["prior_gpa_band"]) - BANDS)
    if unknown_bands:
        raise DataError(f"unknown prior_gpa_band values: {unknown_bands}")
    unknown_terms = sorted(set(frame["term"]) - TERMS)
    if unknown_terms:
        raise DataError(f"unknown term values: {unknown_terms}")

    if not frame[TARGET].isin([0, 1]).all():
        raise DataError(f"{TARGET} must contain only 0 and 1")
    if frame[TARGET].nunique() < 2:
        raise DataError(f"{TARGET} has a single class; a classifier cannot be fitted")

    if frame[NUMERIC].isna().any().any():
        counts = frame[NUMERIC].isna().sum()
        raise DataError(f"null values in numeric columns: {counts[counts > 0].to_dict()}")

    out_of_range = {
        "attendance_rate": (frame["attendance_rate"].between(0, 1)),
        "lms_logins_week": (frame["lms_logins_week"] >= 0),
        "assignments_submitted": (frame["assignments_submitted"].between(0, 12)),
        "support_contacts": (frame["support_contacts"].between(0, 3)),
    }
    bad = [name for name, ok in out_of_range.items() if not ok.all()]
    if bad:
        raise DataError(f"values outside the documented range: {bad}")


def split(
    frame: pd.DataFrame, test_size: float = 0.25, seed: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Stratified split that drops the identifier before returning features.

    Stratification matters here: the positive class is about a quarter of the
    rows, and an unlucky unstratified split can put almost none of it in the
    test set, which makes every metric noisy.
    """
    from sklearn.model_selection import train_test_split

    train, test = train_test_split(
        frame, test_size=test_size, random_state=seed, stratify=frame[TARGET]
    )
    return train.reset_index(drop=True), test.reset_index(drop=True)


def feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Features only. The identifier and the target are never model inputs."""
    return frame[[*NUMERIC, *CATEGORICAL]].copy()

"""Reference solution for Lab 07: no target feature, grouped split, train-only fit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GroupShuffleSplit

DATA = Path("data/students.csv")
FEATURES = ["hours", "prior_score", "sleep_hours"]  # score_band removed
TARGET = "score"


def run(seed: int = 42) -> dict:
    frame = pd.read_csv(DATA)

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=seed)
    train_index, test_index = next(splitter.split(frame, groups=frame["student_id"]))
    train, test = frame.iloc[train_index], frame.iloc[test_index]

    # Fit on training rows only; a mean taken over test rows is information
    # the model would not have when the session is first seen.
    imputer = SimpleImputer(strategy="mean").fit(train[FEATURES])
    model = RandomForestRegressor(n_estimators=120, max_depth=10, random_state=seed)
    model.fit(imputer.transform(train[FEATURES]), train[TARGET])
    predictions = model.predict(imputer.transform(test[FEATURES]))

    return {
        "mae": round(float(mean_absolute_error(test[TARGET], predictions)), 4),
        "features": list(FEATURES),
        "train_groups": sorted(train["student_id"].unique()),
        "test_groups": sorted(test["student_id"].unique()),
        "rows_train": int(len(train)),
        "rows_test": int(len(test)),
        "imputer_fit_rows": int(len(train)),
    }

"""The pipeline as it runs today. Frozen: your tests are checked against it.

Three leaks in one function:

1. `score_band` is derived from the target and used as a feature.
2. The split is row-wise, so the same student appears in train and test.
3. The imputer is fitted on the whole dataset before the split, so test-set
   values influence the training feature means.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

DATA = Path("data/students.csv")
FEATURES = ["hours", "prior_score", "sleep_hours", "score_band"]
TARGET = "score"


def run(seed: int = 42) -> dict:
    frame = pd.read_csv(DATA)
    frame["score_band"] = frame["score_band"].astype(float)
    imputer = SimpleImputer(strategy="mean").fit(frame[FEATURES])
    imputer_fit_rows = len(frame)  # everything, including what will become test

    train, test = train_test_split(frame, test_size=0.25, random_state=seed)
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
        "imputer_fit_rows": int(imputer_fit_rows),
    }

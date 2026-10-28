"""Lab 01 starter: a working analysis that will not reproduce.

Run it twice and compare the two reports:

    python notebook_v1.py > run-a.txt
    python notebook_v1.py > run-b.txt

Nothing here is wrong statistically. The problem is that three decisions are
left to the machine: the train/test split, the reporting sample, and the order
in which sections are processed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

DATA = Path("data/sessions.csv")


def main() -> None:
    frame = pd.read_csv(DATA)

    # 1. No random_state: a different split on every run.
    train, test = train_test_split(frame, test_size=0.25)

    features = ["hours", "prior_score", "sleep_hours"]
    model = LinearRegression().fit(train[features], train["score"])
    mae = mean_absolute_error(test["score"], model.predict(test[features]))
    print(f"rows: {len(train)} train / {len(test)} test")
    print(f"MAE: {mae:.4f}")

    # 2. No seed on the sample used for the manual review list.
    review = frame.sample(n=5)
    print("review sample: " + ", ".join(review["session_id"]))
    print(f"review mean score: {review['score'].mean():.2f}")

    # 3. Iterating a set: the order depends on the interpreter's hash seed.
    print("sections:")
    for section in {"A", "B", "C"}:
        subset = test[test["section"] == section]
        predicted = model.predict(subset[features])
        print(f"  {section}: n={len(subset)} mae={mean_absolute_error(subset['score'], predicted):.4f}")

    # 4. A coefficient table whose row order follows a dict built from a set.
    coefficients = {name: value for name, value in zip(features, model.coef_, strict=True)}
    print("coefficients: " + json_like(coefficients))


def json_like(values: dict[str, float]) -> str:
    return ", ".join(f"{k}={v:.4f}" for k, v in values.items())


if __name__ == "__main__":
    main()

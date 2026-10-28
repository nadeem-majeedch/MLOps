"""Reference solution for Lab 01.

Four changes, each removable independently:

1. `random_state` on the split, and the seed is a parameter.
2. A seeded `sample`.
3. Sorted section labels instead of set iteration.
4. An explicit column order for the coefficient table, plus stable rounding.

The report is also written through a single `format_report` function so that
"the same inputs produce the same text" is a property you can test.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

DATA = Path("data/sessions.csv")
FEATURES = ["hours", "prior_score", "sleep_hours"]
SECTIONS = ["A", "B", "C"]


def format_report(seed: int) -> str:
    frame = pd.read_csv(DATA)
    train, test = train_test_split(frame, test_size=0.25, random_state=seed)

    model = LinearRegression().fit(train[FEATURES], train["score"])
    mae = mean_absolute_error(test["score"], model.predict(test[FEATURES]))

    review = frame.sample(n=5, random_state=seed).sort_values("session_id")
    lines = [
        f"rows: {len(train)} train / {len(test)} test",
        f"MAE: {mae:.4f}",
        "review sample: " + ", ".join(review["session_id"]),
        f"review mean score: {review['score'].mean():.2f}",
        "sections:",
    ]
    for section in SECTIONS:
        subset = test[test["section"] == section]
        predicted = model.predict(subset[FEATURES])
        lines.append(f"  {section}: n={len(subset)} mae={mean_absolute_error(subset['score'], predicted):.4f}")
    lines.append("coefficients: " + ", ".join(f"{n}={v:.4f}" for n, v in zip(FEATURES, model.coef_, strict=True)))
    return "\n".join(lines)


def main() -> None:
    print(format_report(seed=42))


if __name__ == "__main__":
    main()

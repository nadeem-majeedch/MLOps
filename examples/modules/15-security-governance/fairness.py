"""Measure error and selection rates across groups for the support-risk model.

    python fairness.py
    python fairness.py --data ../../../datasets/generated/study_support.csv

The data is synthetic. `prior_gpa_band` is used here as an example grouping
attribute because it is the only demographic-like field in the dataset; in a
real student-support system you would need an approved, necessary attribute,
a documented purpose, and a privacy review before collecting it at all.

What this script does *not* do: prove the model is fair. It measures one model,
at one threshold, on one split. A disparity number is a reason to ask a
question, not an answer.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA = ROOT / "datasets" / "generated" / "study_support.csv"
GROUP = "prior_gpa_band"
NUMERIC = ["attendance_rate", "lms_logins_week", "assignments_submitted", "support_contacts"]
CATEGORICAL = ["term", GROUP]
TARGET = "needs_support"


def load(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = set(NUMERIC + CATEGORICAL + [TARGET]) - set(frame.columns)
    if missing:
        raise SystemExit(f"{path} is missing columns: {sorted(missing)}")
    return frame


def build_model() -> Pipeline:
    prep = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]
    )
    return Pipeline([("prep", prep), ("model", LogisticRegression(max_iter=1000, random_state=42))])


def group_metrics(frame: pd.DataFrame, group: str) -> pd.DataFrame:
    rows = []
    for value, part in frame.groupby(group, sort=True):
        tn, fp, fn, tp = confusion_matrix(part["y_true"], part["y_pred"], labels=[0, 1]).ravel()
        positives = tp + fn
        negatives = tn + fp
        rows.append(
            {
                "group": value,
                "rows": len(part),
                "positives": positives,
                "selection_rate": (tp + fp) / len(part),
                "tpr": tp / positives if positives else float("nan"),
                "fpr": fp / negatives if negatives else float("nan"),
                "precision": tp / (tp + fp) if (tp + fp) else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--group", default=GROUP, choices=[GROUP, "term"])
    args = parser.parse_args()
    group = args.group

    frame = load(args.data)
    train, test = train_test_split(
        frame, test_size=0.25, random_state=42, stratify=frame[TARGET]
    )
    model = build_model()
    model.fit(train[NUMERIC + CATEGORICAL], train[TARGET])

    scored = test.copy()
    scored["y_true"] = scored[TARGET].astype(int)
    scored["y_pred"] = (model.predict_proba(scored[NUMERIC + CATEGORICAL])[:, 1] >= args.threshold).astype(int)

    overall = group_metrics(scored.assign(**{group: "all"}), group).iloc[0]
    print(f"data            {args.data}")
    print(f"rows            {len(frame)} (train {len(train)}, test {len(test)})")
    print(f"threshold       {args.threshold:.2f}")
    print(
        f"overall         selection {overall['selection_rate']:.3f}  "
        f"TPR {overall['tpr']:.3f}  FPR {overall['fpr']:.3f}  "
        f"precision {overall['precision']:.3f}"
    )
    print()
    table = group_metrics(scored, group)
    print(table.to_string(index=False, float_format=lambda value: f"{value:.3f}"))

    print()
    for metric in ("selection_rate", "tpr", "fpr"):
        values = table[metric].dropna()
        if len(values) < 2:
            continue
        ratio = values.min() / values.max() if values.max() else float("nan")
        print(f"{metric:14} min {values.min():.3f}  max {values.max():.3f}  ratio {ratio:.3f}")

    print()
    print("Read this as a prompt, not a verdict: check row counts, the threshold,")
    print("label quality, and whether the group attribute is a proxy for need.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Build, train, and evaluate the support-risk classifier.

One pipeline object does preprocessing and prediction together. That is the
single most useful structural decision in this template: there is no separate
"prepared" file that can drift away from what the model was trained on, and
serving can reuse the same object.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .data import CATEGORICAL, NUMERIC, TARGET, feature_frame, split


def build_pipeline(kind: str = "logistic", seed: int = 42) -> Pipeline:
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ]
    )
    if kind == "logistic":
        estimator = LogisticRegression(max_iter=1000, random_state=seed)
    elif kind == "forest":
        estimator = RandomForestClassifier(
            n_estimators=200, min_samples_leaf=3, random_state=seed, n_jobs=1
        )
    else:
        raise ValueError(f"unknown model kind {kind!r}; use 'logistic' or 'forest'")
    return Pipeline([("pre", pre), ("model", estimator)])


def evaluate(model: Pipeline, test: pd.DataFrame) -> dict[str, float]:
    probabilities = model.predict_proba(feature_frame(test))[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "accuracy": round(float(accuracy_score(test[TARGET], predictions)), 4),
        "precision": round(float(precision_score(test[TARGET], predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(test[TARGET], predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(test[TARGET], probabilities)), 4),
        "positive_rate": round(float(test[TARGET].mean()), 4),
        "test_rows": int(len(test)),
    }


def train(
    frame: pd.DataFrame,
    output_dir: str | Path = "artifacts",
    kind: str = "logistic",
    seed: int = 42,
    test_size: float = 0.25,
) -> dict:
    """Fit, evaluate, persist the artifact, and return metrics plus metadata."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    train_frame, test_frame = split(frame, test_size=test_size, seed=seed)
    model = build_pipeline(kind, seed=seed).fit(
        feature_frame(train_frame), train_frame[TARGET]
    )
    metrics = evaluate(model, test_frame)

    joblib.dump(model, out / "model.joblib")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    meta = {
        "model_kind": kind,
        "seed": seed,
        "test_size": test_size,
        "train_rows": int(len(train_frame)),
        "features": {"numeric": NUMERIC, "categorical": CATEGORICAL},
        "target": TARGET,
        "metrics": metrics,
    }
    (out / "run_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta

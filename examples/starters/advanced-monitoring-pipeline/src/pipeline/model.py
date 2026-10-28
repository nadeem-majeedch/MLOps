"""Train, evaluate, and persist the failure model.

The evaluation reports a **fixed operating threshold** as well as ROC AUC,
because a maintenance team acts on a threshold, not on a ranking. The threshold
is chosen on the training side and frozen before the test set is touched; the
README asks you to notice what changes if you tune it on test.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .data import FEATURES, GROUP, TARGET, split_by_machine


def build_model(seed: int = 42) -> Pipeline:
    """A scaled logistic regression.

    Deliberately simple. On this data it generalises to unseen machines better
    than a forest, and its coefficients can be read and argued with. That is a
    finding to report, not a reason to hide the forest: try both and compare.
    """
    return Pipeline([
        ("scale", StandardScaler()),
        ("logit", LogisticRegression(max_iter=1000, random_state=seed)),
    ])


def choose_threshold(model: Pipeline, frame: pd.DataFrame, target_recall: float) -> float:
    """Pick an operating threshold on training data to reach a recall target.

    The threshold is chosen **before** the test set is scored, and recorded with
    the metrics. Tuning it on test would make the reported recall optimistic and
    the report dishonest, however good the number looked.
    """
    if not 0.0 < target_recall <= 1.0:
        raise ValueError("target_recall must be in (0, 1]")
    scores = model.predict_proba(frame[FEATURES])[:, 1]
    positives = scores[frame[TARGET] == 1]
    if positives.size == 0:
        raise ValueError("no positive rows in the training data; cannot choose a threshold")
    return float(np.quantile(positives, 1 - target_recall))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate(model, frame: pd.DataFrame, threshold: float) -> dict[str, float]:
    probabilities = model.predict_proba(frame[FEATURES])[:, 1]
    predicted = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(frame[TARGET], predicted, labels=[0, 1]).ravel()
    return {
        "roc_auc": round(float(roc_auc_score(frame[TARGET], probabilities)), 4),
        "pr_auc": round(float(average_precision_score(frame[TARGET], probabilities)), 4),
        "recall": round(float(recall_score(frame[TARGET], predicted, zero_division=0)), 4),
        "precision": round(float(precision_score(frame[TARGET], predicted, zero_division=0)), 4),
        "accuracy": round(float(accuracy_score(frame[TARGET], predicted)), 4),
        "true_positives": int(tp),
        "false_negatives": int(fn),
        "false_positives": int(fp),
        "positive_rate": round(float(frame[TARGET].mean()), 4),
        "test_rows": int(len(frame)),
        "threshold": threshold,
    }


def train(
    frame: pd.DataFrame,
    output_dir: str | Path = "artifacts",
    seed: int = 42,
    target_recall: float = 0.8,
    holdout_machines: int = 2,
) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    train_frame, test_frame = split_by_machine(frame, holdout_machines)
    model = build_model(seed).fit(train_frame[FEATURES], train_frame[TARGET])
    threshold = choose_threshold(model, train_frame, target_recall)
    metrics = evaluate(model, test_frame, threshold)

    artifact = out / "model.joblib"
    joblib.dump(model, artifact)
    meta = {
        "model": "RandomForestClassifier",
        "features": FEATURES,
        "target": TARGET,
        "group": GROUP,
        "params": {
            "seed": seed,
            "target_recall": target_recall,
            "threshold": round(threshold, 4),
        },
        "train_rows": int(len(train_frame)),
        "train_machines": sorted(train_frame[GROUP].unique().tolist()),
        "test_machines": sorted(test_frame[GROUP].unique().tolist()),
        "model_sha256": file_sha256(artifact),
        "versions": {"python": platform.python_version(), "scikit_learn": sklearn.__version__},
        "metrics": metrics,
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    (out / "run_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta

"""Input drift measured with the population stability index (PSI).

PSI compares the distribution of one feature in a reference window with the same
feature in a later window:

    PSI = sum over bins of (current% - reference%) * ln(current% / reference%)

Bins come from the reference quantiles, so each reference bin holds roughly the
same number of rows. That makes the index comparable across features, and it
means a reference with few rows gives unstable bins -- check the row counts
before you trust a value.

Interpretation used here (a common industry rule of thumb, not a law):

| PSI | Reading |
|---|---|
| < 0.10 | no meaningful shift |
| 0.10 - 0.25 | moderate shift; investigate |
| > 0.25 | large shift; act |

A PSI value says **nothing about accuracy**. It says the inputs moved. Whether
the model still works is a separate question that needs labels, which are
usually the thing you do not have yet.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

STABLE = "stable"
WATCH = "watch"
DRIFT = "drift"


def population_stability_index(
    reference: pd.Series, current: pd.Series, bins: int = 10
) -> float:
    reference = reference.dropna().astype(float)
    current = current.dropna().astype(float)
    if reference.empty or current.empty:
        raise ValueError("both series need at least one non-null value")

    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        raise ValueError("the reference series has too few distinct values for ten bins")
    edges[0], edges[-1] = -np.inf, np.inf

    reference_share = np.histogram(reference, bins=edges)[0] / len(reference)
    current_share = np.histogram(current, bins=edges)[0] / len(current)
    reference_share = np.clip(reference_share, 1e-6, None)
    current_share = np.clip(current_share, 1e-6, None)
    return float(np.sum((current_share - reference_share) * np.log(current_share / reference_share)))


def classify(psi: float, threshold: float = 0.25) -> str:
    if psi >= threshold:
        return DRIFT
    if psi >= threshold / 2.5:
        return WATCH
    return STABLE


def report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    features: list[str],
    threshold: float = 0.25,
) -> dict:
    per_feature = {}
    for name in features:
        psi = population_stability_index(reference[name], current[name])
        per_feature[name] = {
            "psi": round(psi, 3),
            "status": classify(psi, threshold),
            "reference_mean": round(float(reference[name].mean()), 2),
            "current_mean": round(float(current[name].mean()), 2),
            "reference_rows": int(reference[name].notna().sum()),
            "current_rows": int(current[name].notna().sum()),
        }

    statuses = {entry["status"] for entry in per_feature.values()}
    verdict = DRIFT if DRIFT in statuses else WATCH if WATCH in statuses else STABLE
    return {
        "thresholds": {"drift": threshold, "watch": round(threshold / 2.5, 2)},
        "features": per_feature,
        "verdict": verdict,
        "drifted": sorted(k for k, v in per_feature.items() if v["status"] == DRIFT),
        "note": "Drift describes inputs, not accuracy. Accuracy needs labels.",
    }

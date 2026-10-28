"""Train the artifact the service will load.

    python make_model.py

Writes `models/model.joblib` and `models/meta.json`. The metadata is part of the
contract: the service reports the version it loaded, and the test suite checks
that the API and the artifact agree.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

DATA = Path("data/sessions.csv")
OUT = Path("models")
FEATURES = ["hours", "prior_score", "sleep_hours"]


def main() -> None:
    frame = pd.read_csv(DATA)
    train, test = train_test_split(frame, test_size=0.25, random_state=42)
    model = RandomForestRegressor(n_estimators=150, max_depth=9, random_state=42)
    model.fit(train[FEATURES], train["score"])
    mae = mean_absolute_error(test["score"], model.predict(test[FEATURES]))

    OUT.mkdir(exist_ok=True)
    joblib.dump(model, OUT / "model.joblib")
    meta = {
        "version": f"{date.today():%Y.%m}.1",
        "features": FEATURES,
        "trained_rows": int(len(train)),
        "held_out_mae": round(float(mae), 4),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"wrote model {meta['version']} held-out mae {meta['held_out_mae']}")


if __name__ == "__main__":
    main()

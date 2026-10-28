"""Fixtures: a generated dataset, a temporary model, and a live test client.

The tests never use `artifacts/model.joblib`. A stale artifact from a previous
experiment would make the suite pass or fail for reasons unrelated to the code,
which is the opposite of what a test is for.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture(scope="session")
def data_file(tmp_path_factory) -> Path:
    from make_data import build_rows, COLUMNS
    import csv

    path = tmp_path_factory.mktemp("data") / "trips.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(build_rows(240, seed=11))
    return path


@pytest.fixture(scope="session")
def model_dir(tmp_path_factory, data_file) -> Path:
    from eta_service.train import train

    out = tmp_path_factory.mktemp("model")
    train(data_file, out, seed=42, n_estimators=40)
    return out


@pytest.fixture()
def client(model_dir, monkeypatch):
    from fastapi.testclient import TestClient

    monkeypatch.setenv("MODEL_PATH", str(model_dir / "model.joblib"))
    monkeypatch.setenv("META_PATH", str(model_dir / "run_meta.json"))

    from service.app import app

    with TestClient(app) as test_client:
        yield test_client

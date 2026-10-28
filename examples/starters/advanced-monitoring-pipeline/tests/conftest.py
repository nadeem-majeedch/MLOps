"""Fixtures: import paths and a generated dataset for the session."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture(scope="session")
def generated_dir(tmp_path_factory) -> Path:
    import make_data

    out = tmp_path_factory.mktemp("data")
    make_data.write_labeled(out / "equipment.csv", 240, seed=19)
    make_data.write_batch(out / "current_batch.csv", 80, seed=20)
    return out


@pytest.fixture(scope="session")
def equipment_frame(generated_dir) -> pd.DataFrame:
    return pd.read_csv(generated_dir / "equipment.csv")


@pytest.fixture()
def frame(equipment_frame) -> pd.DataFrame:
    return equipment_frame.copy()

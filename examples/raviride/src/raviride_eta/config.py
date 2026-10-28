"""Paths and parameter loading. Every other module imports this, not the CWD."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PARAMS_PATH = PROJECT_ROOT / "params.yaml"


@lru_cache(maxsize=1)
def load_params(path: Path | None = None) -> dict:
    with open(path or PARAMS_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def project_path(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)

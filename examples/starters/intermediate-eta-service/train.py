"""Train the ETA model used by the service.

    python make_data.py
    python train.py
    python train.py --config config.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from eta_service.train import train  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    data_path = ROOT / config["data"]
    output_dir = ROOT / config["output"]

    if not data_path.exists():
        print(f"no data at {data_path}; run `python make_data.py` first")
        return 1

    meta = train(
        data_path,
        output_dir,
        seed=int(config["seed"]),
        test_size=float(config["test_size"]),
        n_estimators=int(config["n_estimators"]),
    )
    metrics = meta["metrics"]
    print(f"trained on   {meta['train_rows']} rows")
    print(f"MAE          {metrics['mae']:.3f} min")
    print(f"baseline MAE {metrics['baseline_mae']:.3f} min")
    print(f"RMSE         {metrics['rmse']:.3f} min")
    print(f"artifact     {output_dir / 'model.joblib'}")
    print(f"data sha256  {meta['data_sha256'][:16]}...")

    ceiling = float(config.get("max_mae", 999))
    if metrics["mae"] > ceiling:
        print(f"FAIL: MAE {metrics['mae']:.3f} exceeds the ceiling {ceiling:.3f}")
        return 1
    print(f"PASS: MAE {metrics['mae']:.3f} <= ceiling {ceiling:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

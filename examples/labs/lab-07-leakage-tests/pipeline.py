"""Lab 07: the pipeline you will fix.

Today this simply re-exports the frozen production module, so every test you
write behaves exactly as it would against the code running in production.

    python -c "import pipeline; print(pipeline.run()['mae'])"

Replace the re-export with your own `run(seed=42)` that keeps the same return
contract:

    {"mae": float, "features": [str], "train_groups": [str],
     "test_groups": [str], "rows_train": int, "rows_test": int,
     "imputer_fit_rows": int}

Your tests live in `tests/test_leakage.py`. They must fail against
`leaky_pipeline.py` (importable as `leaky_pipeline`) and pass against yours.
`check_lab07.py` does exactly that, twice.
"""

from leaky_pipeline import run  # noqa: F401

__all__ = ["run"]

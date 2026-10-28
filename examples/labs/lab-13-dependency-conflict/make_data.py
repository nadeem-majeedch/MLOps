"""Two extracts, as the reporting service used to receive them.

    python make_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from make_sessions import make  # noqa: E402


def main() -> None:
    out = Path("data")
    out.mkdir(exist_ok=True)

    main_frame = make(rows=480, seed=11)
    main_frame.to_csv(out / "sessions.csv", index=False)

    extra = make(rows=120, seed=12)
    extra["session_id"] = [f"E{i:04d}" for i in range(1, len(extra) + 1)]
    extra.to_csv(out / "extra_sessions.csv", index=False)
    print(f"sessions.csv {len(main_frame)} rows, extra_sessions.csv {len(extra)} rows")


if __name__ == "__main__":
    main()

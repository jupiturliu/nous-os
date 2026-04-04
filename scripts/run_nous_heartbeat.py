#!/usr/bin/env python3
"""Formal entrypoint for the NOUS OS heartbeat bridge."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

from nousos_heartbeat_demo import run_heartbeat_flow


def main() -> None:
    snapshot = run_heartbeat_flow()
    metrics = snapshot["metrics"]
    print("NOUS heartbeat completed")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(snapshot["paths"]["dashboard_data"])


if __name__ == "__main__":
    main()

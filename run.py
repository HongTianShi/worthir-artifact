#!/usr/bin/env python3
"""Run the reusable WorthIR framework example and integrity checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "reproduced" / "framework",
    )
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise SystemExit("WorthIR requires Python 3.10 or newer.")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = output / "validation.json"
    command = [
        sys.executable,
        str(ROOT / "scripts" / "validate_framework.py"),
        "--root",
        str(ROOT),
        "--output",
        str(report),
    ]
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)
    result = json.loads(report.read_text(encoding="utf-8"))
    if result.get("status") != "PASS":
        raise SystemExit(f"Validation failed; see {report}")
    print("PASS: WorthIR framework is ready")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()

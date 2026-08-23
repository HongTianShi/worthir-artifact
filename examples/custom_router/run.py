#!/usr/bin/env python3
"""Build the custom task, run the example router, and compare its utility."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT if (ROOT / "paper_results").is_dir() else Path.cwd()
DESTINATION = OUTPUT_ROOT / "reproduced" / "custom_task"
CHOICES = OUTPUT_ROOT / "reproduced" / "custom_router_choices.csv"


def run(*arguments: str) -> None:
    launcher = (
        [sys.executable, str(ROOT / "worthir.py")]
        if (ROOT / "worthir.py").is_file()
        else [sys.executable, "-m", "worthir"]
    )
    completed = subprocess.run([*launcher, *arguments])
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> None:
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    run(
        "build-custom",
        str(ROOT / "examples" / "custom_task" / "source"),
        str(DESTINATION),
    )
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("router.py")),
            str(DESTINATION),
            str(CHOICES),
        ],
        check=True,
    )
    run(
        "evaluate",
        str(DESTINATION),
        str(CHOICES),
        "--policy-id",
        "example-rule-router",
    )
    print(f"OPEN: {DESTINATION / 'comparison.md'}")


if __name__ == "__main__":
    main()

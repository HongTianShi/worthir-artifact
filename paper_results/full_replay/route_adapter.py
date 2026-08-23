#!/usr/bin/env python3
"""Template adapter between an upstream retrieval pipeline and WorthIR CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    raise SystemExit(
        "This is an adapter boundary, not a bundled retrieval pipeline. Replace "
        f"{Path(__file__).name} in the replay workspace with the task-specific "
        "route runner described by the task guide. It must write task.json, "
        "queries.csv, routes.csv, and outcomes.csv to --output; honor --limit "
        "for the 20-query smoke run; and never use evaluation outcomes to choose routes."
    )


if __name__ == "__main__":
    main()

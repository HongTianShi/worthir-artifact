#!/usr/bin/env python3
"""Verify the compact FEVER replay structure."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=Path, default=Path(__file__).parents[1])
    args = parser.parse_args()
    root = args.bundle_root.resolve()
    required = [
        root / "participant" / "legal_state.parquet",
        root / "participant" / "action_template.csv",
        root / "organizer_private" / "official_dev_test_membership.parquet",
        root / "organizer_private" / "route_costs.parquet",
        root / "organizer_private" / "test_outcomes.parquet",
        root / "frozen_results" / "registered_actions_lambda08.csv",
        root / "frozen_results" / "replayed_score_lambda08.json",
        root / "scripts" / "score_actions.py",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    empty = [
        str(path.relative_to(root))
        for path in required
        if path.is_file() and path.stat().st_size == 0
    ]
    if missing or empty:
        details = []
        if missing:
            details.append(f"missing={missing}")
        if empty:
            details.append(f"empty={empty}")
        raise SystemExit("; ".join(details))
    print(f"PASS: {len(required)} required FEVER replay files")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create the exact FEVER test action template from the legal-state bundle."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    state = pd.read_parquet(args.bundle_root / "participant" / "legal_state.parquet")
    state = state[state["evaluation_role"] == "official_dev_test"]
    if len(state) != 13332 or state["query_uid"].duplicated().any():
        raise SystemExit("unexpected legal-state membership")
    out = state[["query_uid"]].sort_values("query_uid").copy()
    out["selected_route"] = ""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()

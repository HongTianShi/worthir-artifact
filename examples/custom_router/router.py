#!/usr/bin/env python3
"""Example external router that reads only participant-visible task state."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def choose_route(row: dict[str, str]) -> str:
    """Replace this function with a model or any deterministic policy."""

    if row["contains_product_code"].lower() == "true":
        return "combined_review"
    if int(row["question_length"]) > 20:
        return "semantic_search"
    return "keyword_search"


def route(legal_state: Path, output: Path) -> Path:
    with legal_state.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    decisions = [
        {
            "query_uid": row["query_uid"],
            "selected_route_id": choose_route(row),
        }
        for row in rows
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["query_uid", "selected_route_id"]
        )
        writer.writeheader()
        writer.writerows(decisions)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create route choices without reading evaluator outcomes."
    )
    parser.add_argument("legal_state", type=Path, help="participant/legal_state.csv")
    parser.add_argument("output", type=Path, help="choice CSV to create")
    args = parser.parse_args()
    print(f"WROTE: {route(args.legal_state, args.output)}")


if __name__ == "__main__":
    main()

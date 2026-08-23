#!/usr/bin/env python3
"""Run the dependency-free WorthIR smoke test."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from worthir_eval import load_and_score  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reproduced" / "smoke_score.json",
    )
    args = parser.parse_args()
    result = load_and_score(
        ROOT / "contracts" / "quickstart_contract.json",
        ROOT / "quickstart" / "evaluator" / "hidden_ledger.csv",
        ROOT / "quickstart" / "participant" / "example_actions.json",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "queries": result["queries"],
                "mean_utility": result["mean_utility"],
                "mean_exact_within_route_set_regret": result[
                    "mean_exact_within_route_set_regret"
                ],
                "output": str(args.output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate a complete WorthIR task and summarize its contents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from worthir_eval import ScoreError, inspect_task  # noqa: E402


def validate(task: Path) -> dict:
    task = task.resolve()
    return inspect_task(
        task / "contracts" / "task_contract.json",
        task / "evaluator" / "ledger.csv",
        task / "participant" / "legal_state.csv",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path, help="WorthIR task directory")
    parser.add_argument(
        "--output", type=Path, help="optional JSON file for the validation summary"
    )
    args = parser.parse_args()
    try:
        summary = validate(args.task_dir)
    except (ScoreError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    metric = summary["metric"]["name"]
    cost_mode = "query-dependent" if summary["query_dependent_cost"] else "fixed by route"
    print(
        "VALID TASK\n"
        f"  task: {summary['task_id']}\n"
        f"  queries: {summary['queries']}\n"
        f"  routes: {summary['routes']}\n"
        f"  query-route outcomes: {summary['query_route_rows']}\n"
        f"  effectiveness measure: {metric}\n"
        f"  cost mode: {cost_mode}\n"
        f"  cost availability: {summary['cost_availability']}\n"
        f"  public cost source: {summary['public_cost_source']}\n"
        f"  prerequisite edges: {summary['prerequisite_edges']}\n"
        f"  fixed reference: {summary['development_selected_fixed_route']}"
    )


if __name__ == "__main__":
    main()

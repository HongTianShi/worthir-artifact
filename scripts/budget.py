#!/usr/bin/env python3
"""Measure effectiveness and feasibility under hard per-query cost ceilings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from worthir_eval import ScoreError, budget_analysis  # noqa: E402

try:
    from .organizer_io import declared_grid, output_path, parse_grid, same_grid, write_metadata, write_rows
except ImportError:
    from organizer_io import declared_grid, output_path, parse_grid, same_grid, write_metadata, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path, help="WorthIR task directory")
    parser.add_argument("--actions", type=Path, help="frozen action JSON")
    parser.add_argument(
        "--budgets",
        help="comma-separated ceilings; defaults to cost_profile.budget_grid",
    )
    parser.add_argument("--output", type=Path, help="private CSV or Parquet output")
    args = parser.parse_args()
    try:
        if args.budgets:
            grid = parse_grid(args.budgets, "budgets")
            try:
                declared = declared_grid(args.task_dir, "budget_grid")
            except ValueError:
                declared = []
        else:
            declared = declared_grid(args.task_dir, "budget_grid")
            grid = declared
        prespecified = bool(declared) and same_grid(grid, declared)
        destination = output_path(args.task_dir, args.output, "hard_budgets.csv")
        metadata, rows = budget_analysis(args.task_dir, grid, args.actions)
        for row in rows:
            row["prespecified"] = prespecified
            row["scope"] = "evaluator_only"
            row["interpretation"] = "descriptive"
        metadata.update(
            {"prespecified": prespecified, "grid_source": "task_contract" if prespecified else "command_line"}
        )
        write_rows(destination, rows)
        metadata_path = write_metadata(destination, metadata)
    except (ScoreError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(json.dumps({"status": "PASS", "output": str(destination), "metadata": str(metadata_path)}, indent=2))


if __name__ == "__main__":
    main()

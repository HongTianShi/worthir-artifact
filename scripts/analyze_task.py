#!/usr/bin/env python3
"""Write isolated organizer-only per-query routing diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from worthir_eval import ScoreError, per_query_analysis  # noqa: E402

try:
    from .organizer_io import output_path, write_metadata, write_rows
except ImportError:
    from organizer_io import output_path, write_metadata, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path, help="WorthIR task directory")
    parser.add_argument("--actions", type=Path, help="frozen action JSON")
    parser.add_argument(
        "--organizer-output",
        type=Path,
        help="private .csv or .parquet destination",
    )
    args = parser.parse_args()
    try:
        destination = output_path(
            args.task_dir, args.organizer_output, "per_query_scores.csv"
        )
        metadata, rows = per_query_analysis(args.task_dir, args.actions)
        write_rows(destination, rows)
        metadata_path = write_metadata(destination, metadata)
    except (ScoreError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(
        json.dumps(
            {
                "status": "PASS",
                "scope": "evaluator_only",
                "interpretation": "descriptive",
                "rows": len(rows),
                "output": str(destination),
                "metadata": str(metadata_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

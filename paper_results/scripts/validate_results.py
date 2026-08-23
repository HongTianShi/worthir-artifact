#!/usr/bin/env python3
"""Reproduce and validate the released WorthIR paper results."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


def run(command: list[str], root: Path) -> dict[str, Any]:
    started = time.perf_counter()
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        env=environment,
    )
    return {
        "command": command,
        "returncode": process.returncode,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "stdout": process.stdout,
        "stderr": process.stderr,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (
        args.output.resolve()
        if args.output
        else root / "reproduced" / "validation.json"
    )
    required = [
        "analyses/rq2_policy_comparison/actions/non_neural_actions.parquet",
        "analyses/rq3_utility_sources/data/query_strata.csv",
        "analyses/rq4_robustness/data/cost_preference_summary.csv",
        "analyses/rq5_route_value/data/rq5_route_value_prediction_summary.csv",
        "paper_reproduction/inputs/table3_recoverability.csv",
        "replays/fever/scripts/verify_bundle.py",
        "replays/canonical_trec/score_actions.py",
        "full_replay/RESOURCE_REQUIREMENTS.md",
    ]
    missing = [path for path in required if not (root / path).is_file()]
    if missing:
        raise RuntimeError(f"required paper-result files missing: {missing}")

    with tempfile.TemporaryDirectory(prefix="worthir-paper-") as temp:
        work = Path(temp)
        commands = [
            [
                sys.executable,
                str(root / "scripts" / "reproduce_paper.py"),
                "--output-dir",
                str(work / "paper"),
            ],
            [
                sys.executable,
                str(root / "scripts" / "reproduce_rqs.py"),
                "--root",
                str(root),
                "--output-dir",
                str(work / "rqs"),
            ],
            [
                sys.executable,
                str(root / "replays" / "fever" / "scripts" / "verify_bundle.py"),
                "--bundle-root",
                str(root / "replays" / "fever"),
            ],
            [
                sys.executable,
                str(root / "scripts" / "verify_released_canonical.py"),
                "--root",
                str(root / "replays" / "canonical_trec"),
                "--output",
                str(work / "canonical.json"),
            ],
        ]
        started = time.perf_counter()
        results = []
        for command in commands:
            result = run(command, root)
            results.append(result)
            if result["returncode"] != 0:
                break

    status = (
        "PASS"
        if len(results) == 4
        and all(result["returncode"] == 0 for result in results)
        else "FAIL"
    )
    payload = {
        "status": status,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "steps": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "steps": len(results)}, indent=2))
    raise SystemExit(0 if status == "PASS" else 2)


if __name__ == "__main__":
    main()

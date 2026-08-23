#!/usr/bin/env python3
"""Validate the reusable WorthIR scorer and quickstart."""

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
        else root / "reproduced" / "framework" / "validation.json"
    )
    required = [
        "README.md",
        "docs/ADAPT_TO_NEW_TASK.md",
        "contracts/quickstart_contract.json",
        "contracts/route_registry.json",
        "quickstart/participant/legal_state.csv",
        "quickstart/participant/example_actions.json",
        "quickstart/evaluator/hidden_ledger.csv",
        "src/worthir_eval/core.py",
        "task_template/contracts/task_contract.json",
        "scripts/init_task.py",
        "scripts/build_trec_task.py",
        "scripts/build_custom_task.py",
        "scripts/validate_task.py",
        "scripts/actions_from_csv.py",
        "scripts/compare_policies.py",
        "scripts/score_actions.py",
        "worthir.py",
        "setup_environment.py",
        "examples/trec_walkthrough/source/qrels.tsv",
        "examples/trec_walkthrough/source/routes.csv",
        "examples/custom_task/source/task.json",
        "examples/custom_router/router.py",
    ]
    missing = [path for path in required if not (root / path).is_file()]
    if missing:
        raise RuntimeError(f"缺少必要的框架文件：{missing}")

    with tempfile.TemporaryDirectory(prefix="worthir-framework-") as temp:
        work = Path(temp)
        commands = [
            [
                sys.executable,
                str(root / "scripts" / "run_smoke_test.py"),
                "--output",
                str(work / "smoke_score.json"),
            ],
            [
                sys.executable,
                str(root / "scripts" / "run_integrity_tests.py"),
                "--output",
                str(work / "integrity.json"),
            ],
            [
                sys.executable,
                str(root / "scripts" / "init_task.py"),
                str(work / "new_task"),
                "--task-id",
                "validation-task-v1",
            ],
            [
                sys.executable,
                str(root / "scripts" / "score_actions.py"),
                "--task-dir",
                str(work / "new_task"),
                "--output",
                str(work / "template_score.json"),
            ],
            [
                sys.executable,
                str(root / "scripts" / "build_trec_task.py"),
                str(root / "examples" / "trec_walkthrough" / "source"),
                str(work / "trec_task"),
                "--task-id",
                "validation-trec-v1",
                "--metric",
                "ndcg@3",
            ],
            [
                sys.executable,
                str(root / "scripts" / "actions_from_csv.py"),
                "--task-dir",
                str(work / "trec_task"),
                "--input",
                str(
                    root
                    / "examples"
                    / "trec_walkthrough"
                    / "source"
                    / "alternative_choices.csv"
                ),
                "--policy-id",
                "validation-alternative",
            ],
            [
                sys.executable,
                str(root / "scripts" / "compare_policies.py"),
                str(work / "trec_task"),
            ],
            [
                sys.executable,
                str(root / "scripts" / "build_custom_task.py"),
                str(root / "examples" / "custom_task" / "source"),
                str(work / "custom_task"),
            ],
            [
                sys.executable,
                str(root / "scripts" / "validate_task.py"),
                str(work / "custom_task"),
            ],
            [
                sys.executable,
                str(root / "examples" / "custom_router" / "router.py"),
                str(work / "custom_task" / "participant" / "legal_state.csv"),
                str(work / "custom_choices.csv"),
            ],
            [
                sys.executable,
                str(root / "scripts" / "actions_from_csv.py"),
                "--task-dir",
                str(work / "custom_task"),
                "--input",
                str(work / "custom_choices.csv"),
                "--policy-id",
                "validation-custom-router",
            ],
            [
                sys.executable,
                str(root / "scripts" / "compare_policies.py"),
                str(work / "custom_task"),
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
        if len(results) == 12
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

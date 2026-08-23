#!/usr/bin/env python3
"""Human-facing command line for building, scoring, and comparing WorthIR tasks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _run(script: str, arguments: list[str]) -> None:
    command = [sys.executable, str(ROOT / script), *arguments]
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build, score, and compare cost-aware retrieval-routing tasks."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="check the local framework installation")

    init = subparsers.add_parser("init", help="create an editable example task")
    init.add_argument("task_dir", type=Path)
    init.add_argument("--task-id", required=True)

    build = subparsers.add_parser(
        "build-trec", help="build a task from qrels, TREC runs, and costs"
    )
    build.add_argument("source_dir", type=Path)
    build.add_argument("task_dir", type=Path)
    build.add_argument("--task-id", required=True)
    build.add_argument("--metric", default="ndcg@10")
    build.add_argument("--lambda", dest="lam", type=float, default=0.08)
    build.add_argument(
        "--policy-id",
        default="provided-policy",
        help="name for policy_choices.csv when that file is present",
    )

    actions = subparsers.add_parser(
        "actions", help="convert query-route choices from CSV to actions JSON"
    )
    actions.add_argument("task_dir", type=Path)
    actions.add_argument("choice_csv", type=Path)
    actions.add_argument("--policy-id", required=True)
    actions.add_argument("--output", type=Path)

    score = subparsers.add_parser("score", help="score the task's default policy")
    score.add_argument("task_dir", type=Path)
    score.add_argument("--actions", type=Path)
    score.add_argument("--output", type=Path)

    compare = subparsers.add_parser(
        "compare", help="compare policies with all registered fixed routes"
    )
    compare.add_argument("task_dir", type=Path)
    compare.add_argument("--output-dir", type=Path)

    subparsers.add_parser(
        "demo", help="run the complete qrels-to-report walkthrough"
    )

    args = parser.parse_args()
    if args.command == "doctor":
        _run("run.py", [])
    elif args.command == "init":
        _run(
            "scripts/init_task.py",
            [str(args.task_dir), "--task-id", args.task_id],
        )
    elif args.command == "build-trec":
        _run(
            "scripts/build_trec_task.py",
            [
                str(args.source_dir),
                str(args.task_dir),
                "--task-id",
                args.task_id,
                "--metric",
                args.metric,
                "--lambda",
                str(args.lam),
                "--policy-id",
                args.policy_id,
            ],
        )
        launcher = ".\\worthir.cmd" if sys.platform == "win32" else "./worthir"
        print(f'NEXT: {launcher} compare "{args.task_dir}"')
    elif args.command == "actions":
        command = [
            "--task-dir",
            str(args.task_dir),
            "--input",
            str(args.choice_csv),
            "--policy-id",
            args.policy_id,
        ]
        if args.output:
            command.extend(["--output", str(args.output)])
        _run("scripts/actions_from_csv.py", command)
    elif args.command == "score":
        command = ["--task-dir", str(args.task_dir)]
        if args.actions:
            command.extend(["--actions", str(args.actions)])
        if args.output:
            command.extend(["--output", str(args.output)])
        _run("scripts/score_actions.py", command)
    elif args.command == "compare":
        command = [str(args.task_dir)]
        if args.output_dir:
            command.extend(["--output-dir", str(args.output_dir)])
        _run("scripts/compare_policies.py", command)
    elif args.command == "demo":
        destination = ROOT / "reproduced" / "trec_walkthrough"
        reproduced_root = (ROOT / "reproduced").resolve()
        if destination.resolve().parent != reproduced_root:
            raise SystemExit("invalid demo output location")
        if destination.exists():
            shutil.rmtree(destination)
        _run(
            "scripts/build_trec_task.py",
            [
                str(ROOT / "examples" / "trec_walkthrough" / "source"),
                str(destination),
                "--task-id",
                "trec-walkthrough-v1",
                "--metric",
                "ndcg@3",
                "--lambda",
                "0.08",
            ],
        )
        _run("scripts/compare_policies.py", [str(destination)])
        print(f"OPEN: {destination / 'comparison.md'}")


if __name__ == "__main__":
    main()

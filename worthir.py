#!/usr/bin/env python3
"""Human-facing command line for building, scoring, and comparing WorthIR tasks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


CALLER_CWD = Path.cwd()
ROOT = Path(__file__).resolve().parent
if not (ROOT / "scripts").is_dir():
    import worthir_eval

    ROOT = Path(worthir_eval.__file__).resolve().parent
OUTPUT_ROOT = ROOT if (ROOT / "paper_results").is_dir() else Path.cwd()


def _run(script: str, arguments: list[str]) -> None:
    command = [sys.executable, str(ROOT / script), *arguments]
    completed = subprocess.run(command, cwd=CALLER_CWD)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build, score, and compare cost-aware retrieval-routing tasks."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="check the local framework installation")

    init = subparsers.add_parser("init", help="create an editable example task")
    init.add_argument("task_dir", type=Path, help="new task directory")
    init.add_argument("--task-id", required=True, help="stable identifier for the task")

    build = subparsers.add_parser(
        "build-trec", help="build a task from qrels, TREC runs, and costs"
    )
    build.add_argument("source_dir", type=Path, help="qrels, route table, and run files")
    build.add_argument("task_dir", type=Path, help="new WorthIR task directory")
    build.add_argument("--task-id", required=True, help="stable identifier for the task")
    build.add_argument("--metric", default="ndcg@10", help="NDCG measure, such as ndcg@10")
    build.add_argument(
        "--lambda", dest="lam", type=float, default=0.08,
        help="cost preference used in U = effectiveness - lambda * cost",
    )
    build.add_argument(
        "--policy-id",
        default="provided-policy",
        help="name for policy_choices.csv when that file is present",
    )
    build.add_argument(
        "--cost-availability",
        choices=["known_at_commitment", "measured_after_execution"],
        default="known_at_commitment",
        help="when costs become visible to the routing policy",
    )

    actions = subparsers.add_parser(
        "actions", help="convert query-route choices from CSV to actions JSON"
    )
    custom = subparsers.add_parser(
        "build-custom", help="build any task from query, route, and outcome tables"
    )
    custom.add_argument("source_dir", type=Path, help="directory with task.json and CSV inputs")
    custom.add_argument("task_dir", type=Path, help="new WorthIR task directory")
    custom.add_argument(
        "--policy-id", default="provided-policy", help="name for optional policy_choices.csv"
    )

    validate = subparsers.add_parser(
        "validate-task", help="check coverage, contracts, dependencies, and costs"
    )
    validate.add_argument("task_dir", type=Path, help="WorthIR task directory")
    validate.add_argument("--output", type=Path, help="optional JSON validation report")

    actions.add_argument("task_dir", type=Path, help="WorthIR task directory")
    actions.add_argument("choice_csv", type=Path, help="CSV with query_uid and selected_route_id")
    actions.add_argument("--policy-id", required=True, help="identifier recorded in the action file")
    actions.add_argument("--output", type=Path, help="action JSON destination")

    score = subparsers.add_parser("score", help="score the task's default policy")
    score.add_argument("task_dir", type=Path, help="WorthIR task directory")
    score.add_argument("--actions", type=Path, help="action JSON; defaults to participant/actions.json")
    score.add_argument("--output", type=Path, help="score JSON destination")

    compare = subparsers.add_parser(
        "compare", help="compare policies with all registered fixed routes"
    )
    compare.add_argument("task_dir", type=Path, help="WorthIR task directory")
    compare.add_argument("--output-dir", type=Path, help="report destination; defaults to task directory")

    evaluate = subparsers.add_parser(
        "evaluate", help="bind a choice CSV and compare it with all fixed routes"
    )
    evaluate.add_argument("task_dir", type=Path, help="WorthIR task directory")
    evaluate.add_argument("choice_csv", type=Path, help="router output CSV")
    evaluate.add_argument("--policy-id", required=True, help="identifier for the router")
    evaluate.add_argument("--output-dir", type=Path, help="report destination")

    subparsers.add_parser(
        "demo", help="run the complete qrels-to-report walkthrough"
    )
    subparsers.add_parser(
        "demo-custom", help="run the non-TREC custom-task and router walkthrough"
    )

    args = parser.parse_args()
    if args.command == "doctor":
        _run(
            "scripts/validate_framework.py",
            ["--output", str(OUTPUT_ROOT / "reproduced" / "framework" / "validation.json")],
        )
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
                "--cost-availability",
                args.cost_availability,
            ],
        )
        launcher = ".\\worthir.cmd" if sys.platform == "win32" else "./worthir"
        print(f'NEXT: {launcher} compare "{args.task_dir}"')
    elif args.command == "build-custom":
        _run(
            "scripts/build_custom_task.py",
            [
                str(args.source_dir),
                str(args.task_dir),
                "--policy-id",
                args.policy_id,
            ],
        )
        launcher = ".\\worthir.cmd" if sys.platform == "win32" else "./worthir"
        print(f'NEXT: {launcher} validate-task "{args.task_dir}"')
    elif args.command == "validate-task":
        command = [str(args.task_dir)]
        if args.output:
            command.extend(["--output", str(args.output)])
        _run("scripts/validate_task.py", command)
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
    elif args.command == "evaluate":
        action_path = (
            args.task_dir / "participant" / "policies" / f"{args.policy_id}.json"
        )
        _run(
            "scripts/actions_from_csv.py",
            [
                "--task-dir", str(args.task_dir),
                "--input", str(args.choice_csv),
                "--policy-id", args.policy_id,
                "--output", str(action_path),
            ],
        )
        command = [str(args.task_dir)]
        if args.output_dir:
            command.extend(["--output-dir", str(args.output_dir)])
        _run("scripts/compare_policies.py", command)
    elif args.command == "demo":
        destination = OUTPUT_ROOT / "reproduced" / "trec_walkthrough"
        reproduced_root = (OUTPUT_ROOT / "reproduced").resolve()
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
    elif args.command == "demo-custom":
        _run("examples/custom_router/run.py", [])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""用于构建、评分和比较 WorthIR 任务的命令行。"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"


class ChineseArgumentParser(argparse.ArgumentParser):
    """使用中文显示 argparse 的固定帮助文字。"""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._positionals.title = "位置参数"
        self._optionals.title = "选项"
        for action in self._actions:
            if action.dest == "help":
                action.help = "显示帮助并退出"

    def format_help(self) -> str:
        return super().format_help().replace("usage: ", "用法：", 1)

    def format_usage(self) -> str:
        return super().format_usage().replace("usage: ", "用法：", 1)


def _run(script: str, arguments: list[str]) -> None:
    command = [sys.executable, str(ROOT / script), *arguments]
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> None:
    parser = ChineseArgumentParser(
        description="构建、评分和比较成本感知检索路由任务。"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="检查本地框架安装")

    init = subparsers.add_parser("init", help="创建可编辑的示例任务")
    init.add_argument("task_dir", type=Path, help="新任务目录")
    init.add_argument("--task-id", required=True, help="任务的稳定标识符")

    build = subparsers.add_parser(
        "build-trec", help="根据 qrels、TREC run 和成本构建任务"
    )
    build.add_argument("source_dir", type=Path, help="qrels、路线表和 run 文件")
    build.add_argument("task_dir", type=Path, help="新 WorthIR 任务目录")
    build.add_argument("--task-id", required=True, help="任务的稳定标识符")
    build.add_argument("--metric", default="ndcg@10", help="NDCG 指标，例如 ndcg@10")
    build.add_argument(
        "--lambda", dest="lam", type=float, default=0.08,
        help="效用公式 U = 有效性 - lambda * 成本中的成本偏好",
    )
    build.add_argument(
        "--policy-id",
        default="provided-policy",
        help="提供 policy_choices.csv 时为该策略指定名称",
    )
    build.add_argument(
        "--cost-availability",
        choices=["known_at_commitment", "measured_after_execution"],
        default="known_at_commitment",
        help="路线成本在何时对路由策略可见",
    )

    actions = subparsers.add_parser(
        "actions", help="将 CSV 中的查询--路线选择转换为动作 JSON"
    )

    custom = subparsers.add_parser(
        "build-custom", help="根据查询、路线和结果表构建任意任务"
    )
    custom.add_argument("source_dir", type=Path, help="包含 task.json 和 CSV 输入的目录")
    custom.add_argument("task_dir", type=Path, help="新 WorthIR 任务目录")
    custom.add_argument(
        "--policy-id", default="provided-policy", help="可选 policy_choices.csv 的策略名称"
    )

    validate = subparsers.add_parser(
        "validate-task", help="检查覆盖范围、契约、依赖关系和成本"
    )
    validate.add_argument("task_dir", type=Path, help="WorthIR 任务目录")
    validate.add_argument("--output", type=Path, help="可选的 JSON 校验报告")

    actions.add_argument("task_dir", type=Path, help="WorthIR 任务目录")
    actions.add_argument("choice_csv", type=Path, help="包含 query_uid 和 selected_route_id 的 CSV")
    actions.add_argument("--policy-id", required=True, help="写入动作文件的策略标识符")
    actions.add_argument("--output", type=Path, help="动作 JSON 的输出位置")

    score = subparsers.add_parser("score", help="评估任务的默认策略")
    score.add_argument("task_dir", type=Path, help="WorthIR 任务目录")
    score.add_argument("--actions", type=Path, help="动作 JSON；默认使用 participant/actions.json")
    score.add_argument("--output", type=Path, help="评分 JSON 的输出位置")

    compare = subparsers.add_parser(
        "compare", help="将策略与所有已注册固定路线比较"
    )
    compare.add_argument("task_dir", type=Path, help="WorthIR 任务目录")
    compare.add_argument("--output-dir", type=Path, help="报告目录；默认写入任务目录")

    evaluate = subparsers.add_parser(
        "evaluate", help="绑定路线选择 CSV，并与所有固定路线比较"
    )
    evaluate.add_argument("task_dir", type=Path, help="WorthIR 任务目录")
    evaluate.add_argument("choice_csv", type=Path, help="路由器输出的路线选择 CSV")
    evaluate.add_argument("--policy-id", required=True, help="路由器标识符")
    evaluate.add_argument("--output-dir", type=Path, help="报告输出目录")

    subparsers.add_parser(
        "demo", help="运行从 qrels 到报告的完整示例"
    )
    subparsers.add_parser(
        "demo-custom", help="运行非 TREC 自定义任务和外部路由器示例"
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
                "--cost-availability",
                args.cost_availability,
            ],
        )
        launcher = ".\\worthir.cmd" if sys.platform == "win32" else "./worthir"
        print(f'下一步：{launcher} compare "{args.task_dir}"')
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
        print(f'下一步：{launcher} validate-task "{args.task_dir}"')
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
        destination = ROOT / "reproduced" / "trec_walkthrough"
        reproduced_root = (ROOT / "reproduced").resolve()
        if destination.resolve().parent != reproduced_root:
            raise SystemExit("演示输出位置无效")
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
        print(f"请打开：{destination / 'comparison.md'}")
    elif args.command == "demo-custom":
        _run("examples/custom_router/run.py", [])


if __name__ == "__main__":
    main()

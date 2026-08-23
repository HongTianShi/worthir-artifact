#!/usr/bin/env python3
"""运行五阶段原始路线重建流程。"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]
CARDS = json.loads((ROOT / "task_cards.json").read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def parse_inputs(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"--input 必须采用 NAME=PATH，当前为：{value}")
        name, path = value.split("=", 1)
        if not name.strip() or not path.strip():
            raise SystemExit(f"--input 必须采用 NAME=PATH，当前为：{value}")
        parsed[name.strip()] = str(Path(path).expanduser().resolve())
    return parsed


def config_path(workspace: Path) -> Path:
    return workspace / "replay.json"


def load_config(workspace: Path) -> dict:
    path = config_path(workspace)
    if not path.is_file():
        raise SystemExit(f"请先运行 prepare；缺少 {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def check_inputs(config: dict, card: dict) -> list[str]:
    missing: list[str] = []
    for name in card["required_inputs"]:
        value = config.get("inputs", {}).get(name)
        if not value or not Path(value).exists():
            missing.append(name)
    return missing


def prepare(task: str, workspace: Path, supplied: list[str]) -> None:
    card = CARDS[task]
    workspace.mkdir(parents=True, exist_ok=True)
    path = config_path(workspace)
    if path.is_file():
        config = json.loads(path.read_text(encoding="utf-8"))
        if config.get("task") != task:
            raise SystemExit(f"{workspace} 已配置为任务 {config.get('task')}")
    else:
        config = {
            "task": task,
            "inputs": {},
            "commands": {
                "smoke": [sys.executable, "route_adapter.py", "--config", "{config}", "--output", "{source}", "--limit", "20"],
                "run_routes": [sys.executable, "route_adapter.py", "--config", "{config}", "--output", "{source}"]
            }
        }
        shutil.copy2(ROOT / "route_adapter.py", workspace / "route_adapter.py")
    unknown = sorted(set(parse_inputs(supplied)) - set(card["required_inputs"]))
    if unknown:
        raise SystemExit(f"任务 {task} 不认识这些输入名：{', '.join(unknown)}")
    config["inputs"].update(parse_inputs(supplied))
    write_json(path, config)
    missing = check_inputs(config, card)
    print(f"已准备：{workspace}")
    print(f"任务说明：{ROOT / card['guide']}")
    print("资源估计：" + "；".join(f"{key}={value}" for key, value in card["resources"].items()))
    if missing:
        print("缺少外部输入：")
        for name in missing:
            print(f"  {name}: {card['required_inputs'][name]}")
        print(f"补充路径：python replay.py {task} prepare --workspace {workspace} --input NAME=PATH")
    else:
        print(f"可以继续：python replay.py {task} smoke --workspace {workspace}")


def expanded_command(config: dict, workspace: Path, stage: str) -> list[str]:
    command = config.get("commands", {}).get(stage)
    if not isinstance(command, list) or not command:
        raise SystemExit(f"replay.json 必须定义非空的 commands.{stage} 数组")
    values = {
        "config": str(config_path(workspace)),
        "workspace": str(workspace),
        "source": str(workspace / "source"),
    }
    return [str(token).format(**values) for token in command]


def run_routes(task: str, workspace: Path, stage: str) -> None:
    config = load_config(workspace)
    missing = check_inputs(config, CARDS[task])
    if missing:
        raise SystemExit("缺少外部输入：" + ", ".join(missing))
    source = workspace / "source"
    source.mkdir(parents=True, exist_ok=True)
    command = expanded_command(config, workspace, stage)
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=workspace, check=True)
    required = [source / name for name in ("task.json", "queries.csv", "routes.csv", "outcomes.csv")]
    absent = [path.name for path in required if not path.is_file()]
    if absent:
        raise SystemExit("路线适配器运行完毕，但缺少输出：" + ", ".join(absent))
    print(f"路线输出已就绪：{source}")
    if stage == "smoke":
        smoke_task = build_ledger(workspace, "smoke_task")
        smoke_report = workspace / "smoke_validation.json"
        command = [
            sys.executable,
            str(REPOSITORY / "scripts" / "validate_task.py"),
            str(smoke_task),
            "--output",
            str(smoke_report),
        ]
        subprocess.run(command, cwd=REPOSITORY, check=True)
        result = json.loads(smoke_report.read_text(encoding="utf-8"))
        if result["queries"] > 20:
            raise SystemExit(
                f"Smoke 适配器忽略了 20 查询限制，实际写出 {result['queries']} 个查询"
            )
        print(f"SMOKE PASS：{result['queries']} 个查询，{result['routes']} 条路线")


def build_ledger(workspace: Path, task_name: str = "task") -> Path:
    source = workspace / "source"
    task_dir = workspace / task_name
    command = [
        sys.executable,
        str(REPOSITORY / "scripts" / "build_custom_task.py"),
        str(source),
        str(task_dir),
        "--policy-id",
        "full-replay-default"
    ]
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=REPOSITORY, check=True)
    print(f"LEDGER 已就绪：{task_dir / 'evaluator' / 'ledger.csv'}")
    return task_dir


def verify(task: str, workspace: Path) -> None:
    report = workspace / "verification.json"
    command = [
        sys.executable,
        str(REPOSITORY / "scripts" / "validate_task.py"),
        str(workspace / "task"),
        "--output",
        str(report),
    ]
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=REPOSITORY, check=True)
    result = json.loads(report.read_text(encoding="utf-8"))
    card = CARDS[task]
    if result["queries"] not in card["expected_queries"]:
        raise SystemExit(
            f"查询数 {result['queries']} 与发布版本登记的数量不符："
            f"{card['expected_queries']}"
        )
    if result["routes"] not in card["expected_routes"]:
        raise SystemExit(
            f"路线数 {result['routes']} 与登记数量 {card['expected_routes']} 不符"
        )
    result["release_shape_check"] = "PASS"
    result["note"] = (
        "这里检查重建 ledger 的契约和发布版本规模。请用 paper_results/run.py 对发布 ledger 做数值闭合。"
    )
    write_json(report, result)
    print(f"PASS：契约与发布规模检查通过；详见 {report}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=sorted(CARDS))
    parser.add_argument("stage", choices=["prepare", "smoke", "run-routes", "build-ledger", "verify"])
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--input", action="append", default=[], metavar="NAME=PATH")
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    if args.stage == "prepare":
        prepare(args.task, workspace, args.input)
    elif args.stage == "smoke":
        run_routes(args.task, workspace, "smoke")
    elif args.stage == "run-routes":
        run_routes(args.task, workspace, "run_routes")
    elif args.stage == "build-ledger":
        build_ledger(workspace)
    else:
        verify(args.task, workspace)


if __name__ == "__main__":
    main()

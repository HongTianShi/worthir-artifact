#!/usr/bin/env python3
"""根据可运行模板创建自包含的 WorthIR 任务。"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "task_template"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def initialize_task(output: Path, task_id: str) -> Path:
    output = output.resolve()
    if output.exists():
        raise ValueError(f"输出目录已经存在：{output}")
    shutil.copytree(TEMPLATE, output)
    contract_path = output / "contracts" / "task_contract.json"
    action_path = output / "participant" / "actions.json"
    registry_path = output / "contracts" / "route_registry.json"
    contract = read_json(contract_path)
    actions = read_json(action_path)
    registry = read_json(registry_path)
    contract_id = f"{task_id}-contract-v1"
    contract["task_id"] = task_id
    contract["contract_id"] = contract_id
    actions["contract_id"] = contract_id
    registry["registry_id"] = f"{task_id}-routes-v1"
    write_json(contract_path, contract)
    write_json(action_path, actions)
    write_json(registry_path, registry)
    policies = output / "participant" / "policies"
    policies.mkdir()
    (policies / "README.md").write_text(
        "请将其他 WorthIR 动作 JSON 文件放在这里。`worthir compare` 会评估全部文件。\n",
        encoding="utf-8",
    )
    (output / "README.md").write_text(
        f"# {task_id}\n\n该目录是一个可运行的 WorthIR 任务。\n\n"
        "从 WorthIR 仓库根目录运行：\n\n"
        f"```powershell\n.\\worthir.cmd validate-task \"{output}\"\n"
        f".\\worthir.cmd compare \"{output}\"\n```\n\n"
        f"```bash\n./worthir validate-task \"{output}\"\n"
        f"./worthir compare \"{output}\"\n```\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    task_id = args.task_id.strip()
    if not task_id:
        parser.error("--task-id 不能为空")
    try:
        output = initialize_task(args.output, task_id)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"已创建：{output}")
    launcher = ".\\worthir.cmd" if sys.platform == "win32" else "./worthir"
    print(f"下一步：{launcher} validate-task \"{output}\"")


if __name__ == "__main__":
    main()

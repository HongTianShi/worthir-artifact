#!/usr/bin/env python3
"""将便于阅读的路线选择 CSV 转换为绑定到契约的 WorthIR 动作文件。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ActionError(RuntimeError):
    """Raised when route choices do not match a task."""


def convert_actions(task: Path, source: Path, output: Path, policy_id: str) -> Path:
    if not policy_id:
        raise ActionError("policy_id 不能为空")
    task = task.resolve()
    contract_path = task / "contracts" / "task_contract.json"
    registry_path = task / "contracts" / "route_registry.json"
    ledger_path = task / "evaluator" / "ledger.csv"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ActionError(f"无法读取任务契约或路线注册表：{exc}") from exc
    route_ids = {row["route_id"] for row in registry.get("routes", [])}
    with ledger_path.open("r", encoding="utf-8", newline="") as stream:
        query_ids = {row["query_uid"] for row in csv.DictReader(stream)}
    try:
        with source.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["query_uid", "selected_route_id"]:
                raise ActionError(
                    "选择 CSV 必须且只能包含以下列：query_uid, selected_route_id"
                )
            decisions = list(reader)
    except OSError as exc:
        raise ActionError(f"无法读取选择 CSV：{exc}") from exc
    decision_ids = [row["query_uid"] for row in decisions]
    if len(decision_ids) != len(set(decision_ids)):
        raise ActionError("选择 CSV 包含重复的 query_uid")
    if set(decision_ids) != query_ids:
        missing = sorted(query_ids - set(decision_ids))
        extra = sorted(set(decision_ids) - query_ids)
        raise ActionError(f"查询集合不匹配；缺少={missing}，多出={extra}")
    unknown = sorted({row["selected_route_id"] for row in decisions} - route_ids)
    if unknown:
        raise ActionError(f"选择了未知路线：{unknown}")
    payload = {
        "schema_version": contract["action_schema"]["schema_version"],
        "contract_id": contract["contract_id"],
        "policy_id": policy_id,
        "decisions": decisions,
    }
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-dir", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--policy-id", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or (
        args.task_dir / "participant" / "policies" / f"{args.policy_id}.json"
    )
    try:
        written = convert_actions(
            args.task_dir, args.input, output, args.policy_id.strip()
        )
    except ActionError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(f"已写入：{written}")


if __name__ == "__main__":
    main()

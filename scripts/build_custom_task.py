#!/usr/bin/env python3
"""根据通用查询、路线和结果表构建 WorthIR 任务。"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from .launcher import launcher_command
except ImportError:  # 直接运行脚本。
    from launcher import launcher_command


ROOT = Path(__file__).resolve().parents[1]


class BuildError(RuntimeError):
    """通用源文件不能定义有效任务时抛出。"""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"无法读取 {path.name}：{exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"{path.name} 必须包含一个 JSON 对象")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields = list(reader.fieldnames or [])
            rows = list(reader)
    except OSError as exc:
        raise BuildError(f"无法读取 {path.name}：{exc}") from exc
    if not fields:
        raise BuildError(f"{path.name} 缺少表头")
    return fields, rows


def _number(text: str, where: str) -> float:
    try:
        value = float(text)
    except ValueError as exc:
        raise BuildError(f"{where} 必须是数值") from exc
    if not math.isfinite(value):
        raise BuildError(f"{where} 必须是有限数值")
    return value


def _required_object(config: dict[str, Any], name: str) -> dict[str, Any]:
    value = config.get(name)
    if not isinstance(value, dict):
        raise BuildError(f"task.json 必须定义名为 {name} 的对象")
    return value


def _read_queries(source: Path) -> tuple[list[str], list[dict[str, str]], list[str]]:
    fields, rows = _read_csv(source / "queries.csv")
    if fields[0] != "query_uid":
        raise BuildError("queries.csv 必须以 query_uid 列开头")
    query_ids = [row["query_uid"].strip() for row in rows]
    if not query_ids or any(not value for value in query_ids):
        raise BuildError("queries.csv 必须包含非空 query_uid")
    if len(query_ids) != len(set(query_ids)):
        raise BuildError("queries.csv 中存在重复 query_uid")
    for row, query_uid in zip(rows, query_ids):
        row["query_uid"] = query_uid
    return fields, rows, query_ids


def _read_routes(source: Path) -> tuple[list[dict[str, Any]], dict[str, set[str]], str]:
    fields, rows = _read_csv(source / "routes.csv")
    allowed = {
        "route_id",
        "label",
        "prerequisites",
        "cost",
        "incremental_cost",
        "development_selected",
    }
    required = {"route_id", "label", "prerequisites", "development_selected"}
    if not required.issubset(fields) or set(fields) - allowed:
        raise BuildError(
            "routes.csv 必须包含 route_id、label、prerequisites、"
            "development_selected，并且只能选择 cost 或 incremental_cost 其中之一"
        )
    has_cost = "cost" in fields
    has_incremental = "incremental_cost" in fields
    if has_cost == has_incremental:
        raise BuildError("routes.csv 必须且只能包含一种路线成本列")

    route_ids = [row["route_id"].strip() for row in rows]
    if not route_ids or any(not value for value in route_ids):
        raise BuildError("routes.csv 必须包含非空 route_id")
    if len(route_ids) != len(set(route_ids)):
        raise BuildError("routes.csv 中存在重复 route_id")
    route_set = set(route_ids)
    prerequisites: dict[str, set[str]] = {}
    normalized: list[dict[str, Any]] = []
    selected: list[str] = []
    cost_field = "cost" if has_cost else "incremental_cost"
    for line, row in enumerate(rows, 2):
        route_id = row["route_id"].strip()
        required_routes = {
            item.strip()
            for item in row["prerequisites"].split(";")
            if item.strip()
        }
        unknown = sorted(required_routes - route_set)
        if route_id in required_routes:
            raise BuildError(f"routes.csv 第 {line} 行使路线依赖自身")
        if unknown:
            raise BuildError(f"routes.csv 第 {line} 行含有未知前置路线：{unknown}")
        value = _number(row[cost_field], f"routes.csv row {line} {cost_field}")
        if value < 0:
            raise BuildError(f"routes.csv 第 {line} 行的成本为负数")
        if row["development_selected"].strip().lower() in {"1", "true", "yes"}:
            selected.append(route_id)
        prerequisites[route_id] = required_routes
        normalized.append(
            {
                "route_id": route_id,
                "label": row["label"].strip() or route_id,
                "prerequisites": sorted(required_routes),
                cost_field: value,
            }
        )
    if len(selected) != 1:
        raise BuildError("routes.csv 必须且只能标记一条 development_selected 路线")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(route_id: str) -> None:
        if route_id in visiting:
            raise BuildError("路线前置关系中存在环")
        if route_id in visited:
            return
        visiting.add(route_id)
        for prerequisite in prerequisites[route_id]:
            visit(prerequisite)
        visiting.remove(route_id)
        visited.add(route_id)

    for route_id in route_ids:
        visit(route_id)
    return normalized, prerequisites, selected[0]


def _closure(route_id: str, prerequisites: dict[str, set[str]]) -> set[str]:
    result = {route_id}
    for prerequisite in prerequisites[route_id]:
        result.update(_closure(prerequisite, prerequisites))
    return result


def _read_outcomes(
    source: Path,
    query_ids: list[str],
    routes: list[dict[str, Any]],
    prerequisites: dict[str, set[str]],
    metric_minimum: float,
    metric_maximum: float,
) -> list[dict[str, str]]:
    fields, rows = _read_csv(source / "outcomes.csv")
    route_has_cost = "cost" in routes[0]
    allowed = {"query_uid", "route_id", "effectiveness", "cost", "incremental_cost"}
    if not {"query_uid", "route_id", "effectiveness"}.issubset(fields) or set(fields) - allowed:
        raise BuildError(
            "outcomes.csv 必须包含 query_uid、route_id、effectiveness，"
            "并可选包含 cost 或 incremental_cost"
        )
    outcome_cost_fields = [name for name in ("cost", "incremental_cost") if name in fields]
    if len(outcome_cost_fields) > 1:
        raise BuildError("outcomes.csv 不能同时包含 cost 和 incremental_cost")
    outcome_cost_field = outcome_cost_fields[0] if outcome_cost_fields else None
    if outcome_cost_field is not None:
        expected_route_field = "cost" if route_has_cost else "incremental_cost"
        if outcome_cost_field != expected_route_field:
            raise BuildError(
                "routes.csv 和 outcomes.csv 必须使用相同的成本模式"
            )

    query_set = set(query_ids)
    route_ids = [route["route_id"] for route in routes]
    route_set = set(route_ids)
    expected_keys = {(query_uid, route_id) for query_uid in query_ids for route_id in route_ids}
    effectiveness: dict[tuple[str, str], float] = {}
    per_query_values: dict[tuple[str, str], float] = {}
    for line, row in enumerate(rows, 2):
        key = (row["query_uid"].strip(), row["route_id"].strip())
        if key[0] not in query_set or key[1] not in route_set:
            raise BuildError(f"outcomes.csv 第 {line} 行含有未知查询或路线")
        if key in effectiveness:
            raise BuildError(f"outcomes.csv 第 {line} 行重复了查询--路线组合")
        value = _number(row["effectiveness"], f"outcomes.csv row {line} effectiveness")
        if not metric_minimum <= value <= metric_maximum:
            raise BuildError(f"outcomes.csv 第 {line} 行的有效性超出范围")
        effectiveness[key] = value
        if outcome_cost_field is not None:
            cost = _number(row[outcome_cost_field], f"outcomes.csv row {line} cost")
            if cost < 0:
                raise BuildError(f"outcomes.csv 第 {line} 行的成本为负数")
            per_query_values[key] = cost
    if set(effectiveness) != expected_keys:
        missing = len(expected_keys - set(effectiveness))
        extra = len(set(effectiveness) - expected_keys)
        raise BuildError(
            f"outcomes.csv 必须包含每个查询--路线组合；缺少={missing}，多余={extra}"
        )

    constants = {
        route["route_id"]: route["cost" if route_has_cost else "incremental_cost"]
        for route in routes
    }
    ledger_rows: list[dict[str, str]] = []
    for query_uid in query_ids:
        if route_has_cost:
            cumulative = {
                route_id: per_query_values.get((query_uid, route_id), constants[route_id])
                for route_id in route_ids
            }
        else:
            increments = {
                route_id: per_query_values.get((query_uid, route_id), constants[route_id])
                for route_id in route_ids
            }
            cumulative = {
                route_id: sum(increments[item] for item in _closure(route_id, prerequisites))
                for route_id in route_ids
            }
        for route_id in route_ids:
            for prerequisite in prerequisites[route_id]:
                if cumulative[route_id] + 1e-15 < cumulative[prerequisite]:
                    raise BuildError(
                        f"查询 {query_uid} 中路线 {route_id} 的累计成本低于"
                        f"前置路线 {prerequisite}"
                    )
            ledger_rows.append(
                {
                    "query_uid": query_uid,
                    "route_id": route_id,
                    "effectiveness": f"{effectiveness[(query_uid, route_id)]:.12g}",
                    "cost": f"{cumulative[route_id]:.12g}",
                }
            )
    return ledger_rows


def _read_choices(
    source: Path, query_ids: list[str], route_ids: set[str], fixed_route: str, policy_id: str
) -> tuple[str, list[dict[str, str]]]:
    path = source / "policy_choices.csv"
    if not path.is_file():
        return "development-selected-fixed", [
            {"query_uid": query_uid, "selected_route_id": fixed_route}
            for query_uid in query_ids
        ]
    fields, rows = _read_csv(path)
    if fields != ["query_uid", "selected_route_id"]:
        raise BuildError("policy_choices.csv 必须包含 query_uid 和 selected_route_id 两列")
    ids = [row["query_uid"].strip() for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(query_ids):
        raise BuildError("policy_choices.csv 必须包含每个查询且每个只出现一次")
    unknown = sorted({row["selected_route_id"].strip() for row in rows} - route_ids)
    if unknown:
        raise BuildError(f"policy_choices.csv 选择了未知路线：{unknown}")
    return policy_id, [
        {
            "query_uid": row["query_uid"].strip(),
            "selected_route_id": row["selected_route_id"].strip(),
        }
        for row in rows
    ]


def build_task(source: Path, output: Path, policy_id: str) -> Path:
    source = source.resolve()
    output = output.resolve()
    if not source.is_dir():
        raise BuildError(f"源目录不存在：{source}")
    if output.exists():
        raise BuildError(f"输出目录已存在：{output}")
    config = _read_json(source / "task.json")
    task_id = config.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise BuildError("task.json 必须定义非空 task_id")
    metric = _required_object(config, "metric")
    cost_profile = _required_object(config, "cost_profile")
    metric_name = metric.get("name")
    if not isinstance(metric_name, str) or not metric_name.strip():
        raise BuildError("metric.name 不得为空")
    minimum = _number(str(metric.get("minimum")), "metric.minimum")
    maximum = _number(str(metric.get("maximum")), "metric.maximum")
    if minimum >= maximum:
        raise BuildError("metric.minimum 必须小于 metric.maximum")
    if metric.get("higher_is_better", True) is not True:
        raise BuildError("WorthIR 目前要求有效性指标越高越好")
    lam = _number(str(cost_profile.get("lambda")), "cost_profile.lambda")
    if lam < 0:
        raise BuildError("cost_profile.lambda 不得为负")
    profile_id = cost_profile.get("profile_id")
    provenance = cost_profile.get("provenance")
    availability = cost_profile.get("availability", "known_at_commitment")
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise BuildError("cost_profile.profile_id 不得为空")
    if not isinstance(provenance, str) or not provenance.strip():
        raise BuildError("cost_profile.provenance 不得为空")
    if availability not in {"known_at_commitment", "measured_after_execution"}:
        raise BuildError(
            "cost_profile.availability 必须是 known_at_commitment 或 "
            "measured_after_execution"
        )

    legal_fields, legal_rows, query_ids = _read_queries(source)
    routes, prerequisites, fixed_route = _read_routes(source)
    configured_fixed = config.get("development_selected_fixed_route", fixed_route)
    if configured_fixed != fixed_route:
        raise BuildError(
            "task.json 与 routes.csv 中的 development_selected_fixed_route 不一致"
        )
    ledger_rows = _read_outcomes(
        source, query_ids, routes, prerequisites, minimum, maximum
    )
    costs_by_route = {
        route["route_id"]: {
            float(row["cost"])
            for row in ledger_rows
            if row["route_id"] == route["route_id"]
        }
        for route in routes
    }
    cost_mode = (
        "query_dependent"
        if any(len(values) > 1 for values in costs_by_route.values())
        else "fixed"
    )
    policy_id, decisions = _read_choices(
        source, query_ids, {route["route_id"] for route in routes}, fixed_route, policy_id
    )

    output.mkdir(parents=True)
    (output / "contracts").mkdir()
    (output / "participant" / "policies").mkdir(parents=True)
    (output / "evaluator").mkdir()
    with (output / "participant" / "legal_state.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=legal_fields)
        writer.writeheader()
        writer.writerows(legal_rows)
    with (output / "evaluator" / "ledger.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["query_uid", "route_id", "effectiveness", "cost"]
        )
        writer.writeheader()
        writer.writerows(ledger_rows)

    registry_id = f"{task_id}-routes-v1"
    route_costs_file = (
        "../participant/route_costs.csv"
        if availability == "known_at_commitment" and cost_mode == "query_dependent"
        else None
    )
    registry = {
        "schema_version": "worthir-route-registry-v1.2",
        "registry_id": registry_id,
        "cost_information": {
            "availability": availability,
            "mode": cost_mode,
            "route_costs_file": route_costs_file,
        },
        "routes": [
            {
                "route_id": route["route_id"],
                "label": route["label"],
                "prerequisites": route["prerequisites"],
                **(
                    {"cost": next(iter(costs_by_route[route["route_id"]]))}
                    if availability == "known_at_commitment" and cost_mode == "fixed"
                    else {}
                ),
            }
            for route in routes
        ],
    }
    contract_id = f"{task_id}-contract-v1"
    contract = {
        "schema_version": "worthir-contract-v1.0",
        "contract_id": contract_id,
        "task_id": task_id,
        "expected_query_count": len(query_ids),
        "route_registry": "route_registry.json",
        "development_selected_fixed_route": fixed_route,
        "action_schema": {
            "schema_version": "worthir-action-file-v1.0",
            "top_level_fields": ["schema_version", "contract_id", "policy_id", "decisions"],
            "decision_fields": ["query_uid", "selected_route_id"],
        },
        "ledger_schema": {
            "columns": ["query_uid", "route_id", "effectiveness", "cost"]
        },
        "metric": {"name": metric_name, "minimum": minimum, "maximum": maximum},
        "cost_profile": {
            "profile_id": profile_id,
            "provenance": provenance,
            "lambda": lam,
            "availability": availability,
        },
    }
    _write_json(output / "contracts" / "route_registry.json", registry)
    _write_json(output / "contracts" / "task_contract.json", contract)
    if route_costs_file is not None:
        with (output / "participant" / "route_costs.csv").open(
            "w", encoding="utf-8", newline=""
        ) as stream:
            writer = csv.DictWriter(
                stream, fieldnames=["query_uid", "route_id", "cost"]
            )
            writer.writeheader()
            writer.writerows(
                {
                    "query_uid": row["query_uid"],
                    "route_id": row["route_id"],
                    "cost": row["cost"],
                }
                for row in ledger_rows
            )
    _write_json(
        output / "participant" / "actions.json",
        {
            "schema_version": "worthir-action-file-v1.0",
            "contract_id": contract_id,
            "policy_id": policy_id,
            "decisions": decisions,
        },
    )
    shutil.copy2(source / "task.json", output / "evaluator" / "source_task.json")
    (output / ".gitignore").write_text(
        "score.json\ncomparison.csv\ncomparison.json\nfixed_routes.csv\n", encoding="utf-8"
    )
    try:
        task_argument = output.relative_to(ROOT).as_posix()
    except ValueError:
        task_argument = "<path-to-this-task>"
    if route_costs_file is not None:
        cost_note = "逐查询公开成本位于 `participant/route_costs.csv`。\n\n"
    elif availability == "known_at_commitment":
        cost_note = "固定公开成本位于 `contracts/route_registry.json`。\n\n"
    else:
        cost_note = "成本在路线执行后由评价器测量。\n\n"
    powershell_launcher = launcher_command(ROOT, "powershell")
    posix_launcher = launcher_command(ROOT, "posix")
    (output / "README.md").write_text(
        f"# {task_id}\n\n"
        f"成本可见时点：`{availability}`。{cost_note}"
        f"评分前先校验完整任务：\n\n"
        f"```powershell\n{powershell_launcher} validate-task {task_argument}\n```\n\n"
        f"```bash\n{posix_launcher} validate-task {task_argument}\n```\n\n"
        f"然后将默认策略与每条固定路线比较：\n\n"
        f"```powershell\n{powershell_launcher} compare {task_argument}\n```\n\n"
        f"```bash\n{posix_launcher} compare {task_argument}\n```\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source", type=Path, help="包含 task.json 和三个 CSV 文件的目录"
    )
    parser.add_argument("output", type=Path, help="新 WorthIR 任务目录")
    parser.add_argument(
        "--policy-id", default="provided-policy", help="policy_choices.csv 的策略名称"
    )
    args = parser.parse_args()
    try:
        output = build_task(args.source, args.output, args.policy_id.strip())
    except BuildError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(f"已构建：{output}")


if __name__ == "__main__":
    main()

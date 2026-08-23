"""仅使用标准库完成 WorthIR 动作校验和完整路线集合评分。"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


class ScoreError(RuntimeError):
    """契约、动作文件或评价方台账无效时抛出。"""


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScoreError(f"无法读取 JSON 文件 {path.name}：{exc}") from exc
    if not isinstance(payload, dict):
        raise ScoreError(f"{path.name} 必须包含一个 JSON 对象")
    return payload


def _exact_fields(obj: dict[str, Any], fields: list[str], where: str) -> None:
    if set(obj) != set(fields):
        missing = sorted(set(fields) - set(obj))
        extra = sorted(set(obj) - set(fields))
        raise ScoreError(f"{where} 字段不匹配；缺少={missing}，多余={extra}")


def _load_registry(
    contract_path: Path, contract: dict[str, Any]
) -> tuple[str, list[dict[str, Any]], dict[str, Any] | None]:
    registry_name = contract.get("route_registry")
    if not isinstance(registry_name, str) or not registry_name:
        raise ScoreError("契约中的 route_registry 路径格式错误")
    registry_path = contract_path.parent / registry_name
    if not registry_path.is_file():
        raise ScoreError("缺少路线注册表")
    registry = read_json(registry_path)
    registry_id = registry.get("registry_id")
    if not isinstance(registry_id, str) or not registry_id:
        raise ScoreError("路线注册表必须定义非空 registry_id")
    routes = registry.get("routes")
    if not isinstance(routes, list) or not routes:
        raise ScoreError("路线注册表必须包含非空 routes 列表")
    route_ids: list[str] = []
    normalized: list[dict[str, Any]] = []
    prerequisites: dict[str, list[str]] = {}
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            raise ScoreError(f"路线 {index} 的结构无效")
        fields = set(route)
        route_cost = route.get("cost")
        structural_fields = fields - {"cost"}
        if structural_fields == {"route_id", "label", "parent_route_id"}:
            parent = route["parent_route_id"]
            route_prerequisites = [] if parent is None else [parent]
        elif structural_fields == {"route_id", "label", "prerequisites"}:
            route_prerequisites = route["prerequisites"]
            if not isinstance(route_prerequisites, list) or any(
                not isinstance(value, str) or not value
                for value in route_prerequisites
            ):
                raise ScoreError(
                    f"路线 {index} 的 prerequisites 必须是路线 ID 列表"
                )
            if len(route_prerequisites) != len(set(route_prerequisites)):
                raise ScoreError(f"路线 {index} 重复声明了前置路线")
        else:
            raise ScoreError(f"路线 {index} 的结构无效")
        if "cost" in fields:
            if not isinstance(route_cost, (int, float)) or isinstance(route_cost, bool):
                raise ScoreError(f"路线 {index} 的公开成本不是数值")
            route_cost = float(route_cost)
            if not math.isfinite(route_cost) or route_cost < 0:
                raise ScoreError(f"路线 {index} 的公开成本无效")
        route_id = route["route_id"]
        if not isinstance(route_id, str) or not route_id:
            raise ScoreError(f"路线 {index} 的 route_id 无效")
        if not isinstance(route["label"], str) or not route["label"]:
            raise ScoreError(f"路线 {index} 的 label 无效")
        if route_id in prerequisites:
            raise ScoreError(f"route_id 重复：{route_id}")
        route_ids.append(route_id)
        prerequisites[route_id] = list(route_prerequisites)
        normalized.append(
            {
                "route_id": route_id,
                "label": route["label"],
                "prerequisites": list(route_prerequisites),
                "cost": route_cost if "cost" in fields else None,
            }
        )
    route_set = set(route_ids)
    for route_id, required_routes in prerequisites.items():
        unknown = sorted(set(required_routes) - route_set)
        if unknown:
            raise ScoreError(
                f"路线 {route_id} 含有未知前置路线：{unknown}"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(route_id: str) -> None:
        if route_id in visiting:
            raise ScoreError("路线注册表中的前置关系存在环")
        if route_id in visited:
            return
        visiting.add(route_id)
        for prerequisite in prerequisites[route_id]:
            visit(prerequisite)
        visiting.remove(route_id)
        visited.add(route_id)

    for route_id in route_ids:
        visit(route_id)

    cost_information = registry.get("cost_information")
    if cost_information is not None:
        if not isinstance(cost_information, dict):
            raise ScoreError("路线注册表的 cost_information 必须是对象")
        expected = {"availability", "mode", "route_costs_file"}
        if set(cost_information) != expected:
            raise ScoreError(
                "路线注册表的 cost_information 必须包含 availability、"
                "mode 和 route_costs_file"
            )
        if cost_information["availability"] not in {
            "known_at_commitment",
            "measured_after_execution",
        }:
            raise ScoreError("未知的成本可见时点")
        if cost_information["mode"] not in {"fixed", "query_dependent"}:
            raise ScoreError("未知的公开成本模式")
        route_costs_file = cost_information["route_costs_file"]
        if route_costs_file is not None and (
            not isinstance(route_costs_file, str) or not route_costs_file
        ):
            raise ScoreError("route_costs_file 必须为空或非空路径")
    return registry_id, normalized, cost_information


def _validate_public_costs(
    contract_path: Path,
    routes: list[dict[str, Any]],
    cost_information: dict[str, Any] | None,
    matrix: dict[str, dict[str, tuple[float, float]]],
) -> tuple[str, str]:
    """核对参与者可见成本与评价方实际评分成本。"""

    if cost_information is None:
        return "unspecified", "旧版注册表未声明"
    availability = cost_information["availability"]
    mode = cost_information["mode"]
    route_costs_file = cost_information["route_costs_file"]
    route_ids = [route["route_id"] for route in routes]
    actual_mode = "query_dependent" if any(
        len({matrix[query_uid][route_id][1] for query_uid in matrix}) > 1
        for route_id in route_ids
    ) else "fixed"
    if mode != actual_mode:
        raise ScoreError(
            f"声明的成本模式为 {mode}，但评价方成本实际为 {actual_mode}"
        )
    public_route_costs = [route["cost"] for route in routes]
    if availability == "measured_after_execution":
        if any(value is not None for value in public_route_costs) or route_costs_file:
            raise ScoreError("执行后测量的成本不能作为决策时公开成本")
        return availability, "仅评价方台账"
    if mode == "fixed":
        if route_costs_file is not None or any(
            value is None for value in public_route_costs
        ):
            raise ScoreError("决策时已知的固定成本必须写入每条注册路线")
        for route in routes:
            public_cost = float(route["cost"])
            for query_uid in matrix:
                ledger_cost = matrix[query_uid][route["route_id"]][1]
                if not math.isclose(
                    public_cost, ledger_cost, rel_tol=0.0, abs_tol=1e-12
                ):
                    raise ScoreError(
                        f"公开成本不一致：{query_uid}/{route['route_id']}"
                    )
        return availability, "路线注册表"
    if any(value is not None for value in public_route_costs):
        raise ScoreError("逐查询决策时成本必须写入 route_costs.csv")
    if route_costs_file is None:
        raise ScoreError("逐查询决策时成本必须声明 route_costs_file")
    path = (contract_path.parent / route_costs_file).resolve()
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["query_uid", "route_id", "cost"]:
                raise ScoreError(
                    "参与者 route_costs.csv 的列必须为 query_uid、route_id、cost"
                )
            rows = list(reader)
    except OSError as exc:
        raise ScoreError(f"无法读取参与者路线成本：{exc}") from exc
    observed: dict[tuple[str, str], float] = {}
    for index, row in enumerate(rows, 2):
        key = (row["query_uid"], row["route_id"])
        if key in observed or key[0] not in matrix or key[1] not in route_ids:
            raise ScoreError(f"参与者 route_costs.csv 第 {index} 行的键无效")
        try:
            value = float(row["cost"])
        except ValueError as exc:
            raise ScoreError(f"参与者 route_costs.csv 第 {index} 行成本不是数值") from exc
        if not math.isfinite(value) or value < 0:
            raise ScoreError(f"参与者 route_costs.csv 第 {index} 行成本无效")
        observed[key] = value
    expected = {
        (query_uid, route_id) for query_uid in matrix for route_id in route_ids
    }
    if set(observed) != expected:
        missing = len(expected - set(observed))
        extra = len(set(observed) - expected)
        raise ScoreError(f"参与者路线成本不完整；缺少={missing}，多余={extra}")
    for key, public_cost in observed.items():
        if not math.isclose(
            public_cost,
            matrix[key[0]][key[1]][1],
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ScoreError(f"公开成本不一致：{key[0]}/{key[1]}")
    return availability, str(path)


def _load_actions(
    action_path: Path,
    contract_path: Path,
    contract: dict[str, Any],
) -> tuple[str, list[dict[str, str]]]:
    actions = read_json(action_path)
    schema = contract.get("action_schema", {})
    top_fields = schema.get("top_level_fields")
    decision_fields = schema.get("decision_fields")
    if not isinstance(top_fields, list) or not isinstance(decision_fields, list):
        raise ScoreError("契约中的动作结构格式错误")
    _exact_fields(actions, top_fields, "action file")
    if actions["schema_version"] != schema.get("schema_version"):
        raise ScoreError("动作结构版本不匹配")
    if actions["contract_id"] != contract.get("contract_id"):
        raise ScoreError("动作文件的 contract_id 不匹配")
    if not isinstance(actions["policy_id"], str) or not actions["policy_id"]:
        raise ScoreError("policy_id 必须是非空字符串")
    decisions = actions["decisions"]
    if not isinstance(decisions, list):
        raise ScoreError("decisions 必须是列表")
    normalized: list[dict[str, str]] = []
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            raise ScoreError(f"决策 {index} 必须是对象")
        _exact_fields(decision, decision_fields, f"decision {index}")
        query_uid = decision["query_uid"]
        route_id = decision["selected_route_id"]
        if not isinstance(query_uid, str) or not query_uid:
            raise ScoreError(f"决策 {index} 的 query_uid 无效")
        if not isinstance(route_id, str) or not route_id:
            raise ScoreError(f"决策 {index} 的 selected_route_id 无效")
        normalized.append({"query_uid": query_uid, "selected_route_id": route_id})
    return actions["policy_id"], normalized


def _load_ledger(
    ledger_path: Path,
    contract: dict[str, Any],
    route_ids: list[str],
) -> dict[str, dict[str, tuple[float, float]]]:
    expected_columns = contract.get("ledger_schema", {}).get("columns")
    if not isinstance(expected_columns, list):
        raise ScoreError("契约中的台账结构格式错误")
    try:
        with ledger_path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != expected_columns:
                raise ScoreError(
                    f"台账列必须严格为 {expected_columns}，"
                    f"实际为 {reader.fieldnames}"
                )
            rows = list(reader)
    except OSError as exc:
        raise ScoreError(f"无法读取评价方台账：{exc}") from exc
    matrix: dict[str, dict[str, tuple[float, float]]] = {}
    metric = contract["metric"]
    q_min = float(metric["minimum"])
    q_max = float(metric["maximum"])
    for index, row in enumerate(rows):
        query_uid = row["query_uid"]
        route_id = row["route_id"]
        if not query_uid or route_id not in route_ids:
            raise ScoreError(f"台账第 {index} 行的键无效")
        try:
            effectiveness = float(row["effectiveness"])
            cost = float(row["cost"])
        except ValueError as exc:
            raise ScoreError(f"台账第 {index} 行含有非数值字段") from exc
        if not math.isfinite(effectiveness) or not math.isfinite(cost):
            raise ScoreError(f"台账第 {index} 行含有非有限数值")
        if effectiveness < q_min or effectiveness > q_max:
            raise ScoreError(f"台账第 {index} 行的有效性超出范围")
        if cost < 0:
            raise ScoreError(f"台账第 {index} 行的成本为负数")
        by_route = matrix.setdefault(query_uid, {})
        if route_id in by_route:
            raise ScoreError(f"台账键重复：{query_uid}/{route_id}")
        by_route[route_id] = (effectiveness, cost)
    required_routes = set(route_ids)
    for query_uid, by_route in matrix.items():
        if set(by_route) != required_routes:
            missing = sorted(required_routes - set(by_route))
            extra = sorted(set(by_route) - required_routes)
            raise ScoreError(
                f"查询 {query_uid} 的路线集合不完整；"
                f"缺少={missing}，多余={extra}"
            )
    return matrix


def _validate_cumulative_costs(
    matrix: dict[str, dict[str, tuple[float, float]]],
    routes: list[dict[str, Any]],
) -> None:
    if not routes:
        return
    prerequisites = {
        route["route_id"]: route["prerequisites"] for route in routes
    }
    for query_uid, by_route in matrix.items():
        for route_id, required_routes in prerequisites.items():
            for prerequisite in required_routes:
                if by_route[route_id][1] + 1e-15 < by_route[prerequisite][1]:
                    raise ScoreError(
                        f"查询 {query_uid} 的成本并非累计成本：路线 {route_id} "
                        f"比前置路线 {prerequisite} 更便宜"
                    )


def inspect_task(
    contract_path: Path,
    ledger_path: Path,
    legal_state_path: Path | None = None,
) -> dict[str, Any]:
    """评分前校验任务并返回精简摘要。"""

    contract_path = contract_path.resolve()
    ledger_path = ledger_path.resolve()
    contract = read_json(contract_path)
    registry_id, routes, cost_information = _load_registry(contract_path, contract)
    route_ids = [route["route_id"] for route in routes]
    matrix = _load_ledger(ledger_path, contract, route_ids)
    _validate_cumulative_costs(matrix, routes)
    cost_availability, public_cost_source = _validate_public_costs(
        contract_path, routes, cost_information, matrix
    )
    expected_count = int(contract["expected_query_count"])
    if len(matrix) != expected_count:
        raise ScoreError(
            f"台账查询数不匹配：应为 {expected_count}，实际为 {len(matrix)}"
        )

    legal_fields: list[str] = []
    if legal_state_path is not None:
        legal_state_path = legal_state_path.resolve()
        try:
            with legal_state_path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                legal_fields = list(reader.fieldnames or [])
                rows = list(reader)
        except OSError as exc:
            raise ScoreError(f"无法读取参与方合法状态：{exc}") from exc
        if not legal_fields or legal_fields[0] != "query_uid":
            raise ScoreError("参与方合法状态必须以 query_uid 列开头")
        legal_ids = [row["query_uid"] for row in rows]
        if len(legal_ids) != len(set(legal_ids)):
            raise ScoreError("参与方合法状态中存在重复 query_uid")
        if set(legal_ids) != set(matrix):
            missing = sorted(set(matrix) - set(legal_ids))
            extra = sorted(set(legal_ids) - set(matrix))
            raise ScoreError(
                f"参与方合法状态的查询集合不匹配；缺少={missing}，多余={extra}"
            )

    costs_by_route = {
        route_id: {matrix[query_uid][route_id][1] for query_uid in matrix}
        for route_id in route_ids
    }
    prerequisite_edges = sum(len(route["prerequisites"]) for route in routes)
    return {
        "task_id": contract["task_id"],
        "contract_id": contract["contract_id"],
        "registry_id": registry_id,
        "queries": len(matrix),
        "routes": len(routes),
        "query_route_rows": sum(len(rows) for rows in matrix.values()),
        "route_ids": route_ids,
        "prerequisite_edges": prerequisite_edges,
        "query_dependent_cost": any(len(values) > 1 for values in costs_by_route.values()),
        "cost_availability": cost_availability,
        "public_cost_source": public_cost_source,
        "metric": contract["metric"],
        "cost_profile": contract["cost_profile"],
        "development_selected_fixed_route": contract["development_selected_fixed_route"],
        "participant_fields": legal_fields,
    }


def load_and_score(
    contract_path: Path,
    ledger_path: Path,
    action_path: Path,
) -> dict[str, Any]:
    contract_path = contract_path.resolve()
    ledger_path = ledger_path.resolve()
    action_path = action_path.resolve()
    contract = read_json(contract_path)
    registry_id, routes, cost_information = _load_registry(contract_path, contract)
    route_ids = [route["route_id"] for route in routes]
    route_rank = {route_id: index for index, route_id in enumerate(route_ids)}
    fixed_reference = contract.get("development_selected_fixed_route")
    if fixed_reference not in route_rank:
        raise ScoreError(
            "development_selected_fixed_route 必须指向已注册路线"
        )
    policy_id, decisions = _load_actions(action_path, contract_path, contract)
    matrix = _load_ledger(ledger_path, contract, route_ids)
    _validate_cumulative_costs(matrix, routes)
    _validate_public_costs(contract_path, routes, cost_information, matrix)

    expected_count = int(contract["expected_query_count"])
    if len(matrix) != expected_count:
        raise ScoreError(
            f"台账查询数不匹配：应为 {expected_count}，实际为 {len(matrix)}"
        )
    if len(decisions) != expected_count:
        raise ScoreError(
            f"动作数不匹配：应为 {expected_count}，实际为 {len(decisions)}"
        )
    decision_ids = [row["query_uid"] for row in decisions]
    if len(set(decision_ids)) != len(decision_ids):
        raise ScoreError("动作文件中存在重复 query_uid")
    if set(decision_ids) != set(matrix):
        missing = sorted(set(matrix) - set(decision_ids))
        extra = sorted(set(decision_ids) - set(matrix))
        raise ScoreError(f"动作查询集合不匹配；缺少={missing}，多余={extra}")
    unknown_routes = sorted(
        {row["selected_route_id"] for row in decisions} - set(route_ids)
    )
    if unknown_routes:
        raise ScoreError(f"选择了未注册路线：{unknown_routes}")

    lam = float(contract["cost_profile"]["lambda"])
    total_effectiveness = 0.0
    total_cost = 0.0
    total_utility = 0.0
    total_regret = 0.0
    oracle_matches = 0
    shares: Counter[str] = Counter()
    for decision in decisions:
        query_uid = decision["query_uid"]
        selected = decision["selected_route_id"]
        candidates: list[tuple[float, float, int, str]] = []
        for route_id in route_ids:
            effectiveness, cost = matrix[query_uid][route_id]
            utility = effectiveness - lam * cost
            candidates.append((utility, -cost, -route_rank[route_id], route_id))
        oracle_utility, _, _, oracle_route = max(candidates)
        effectiveness, cost = matrix[query_uid][selected]
        utility = effectiveness - lam * cost
        regret = oracle_utility - utility
        if regret < -1e-12:
            raise ScoreError("出现负遗憾值，说明算术结果不一致")
        total_effectiveness += effectiveness
        total_cost += cost
        total_utility += utility
        total_regret += max(regret, 0.0)
        oracle_matches += int(selected == oracle_route)
        shares[selected] += 1

    n_queries = len(decisions)
    return {
        "schema_version": "worthir-aggregate-score-v1.0",
        "task_id": contract["task_id"],
        "contract_id": contract["contract_id"],
        "registry_id": registry_id,
        "policy_id": policy_id,
        "queries": n_queries,
        "metric": contract["metric"]["name"],
        "cost_profile_id": contract["cost_profile"]["profile_id"],
        "cost_profile_provenance": contract["cost_profile"]["provenance"],
        "development_selected_fixed_route": fixed_reference,
        "lambda": lam,
        "mean_effectiveness": round(total_effectiveness / n_queries, 12),
        "mean_cost": round(total_cost / n_queries, 12),
        "mean_utility": round(total_utility / n_queries, 12),
        "mean_exact_within_route_set_regret": round(
            total_regret / n_queries, 12
        ),
        "oracle_match_share": round(oracle_matches / n_queries, 12),
        "action_counts": {route: shares.get(route, 0) for route in route_ids},
        "information_boundary": (
            "actions validated and contract-bound before evaluator ledger join"
        ),
    }

"""组织者专用的逐查询与成本偏好分析。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .core import (
    ScoreError,
    _load_actions,
    _load_ledger,
    _load_registry,
    _validate_cumulative_costs,
    _validate_public_costs,
    read_json,
)


def _load_task(
    task_dir: Path, action_path: Path | None = None
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    dict[str, dict[str, tuple[float, float]]],
    str,
    list[dict[str, str]],
]:
    task = task_dir.resolve()
    contract_path = task / "contracts" / "task_contract.json"
    ledger_path = task / "evaluator" / "ledger.csv"
    action_path = (
        action_path.resolve()
        if action_path is not None
        else task / "participant" / "actions.json"
    )
    contract = read_json(contract_path)
    _, routes, cost_information = _load_registry(contract_path, contract)
    route_ids = [route["route_id"] for route in routes]
    matrix = _load_ledger(ledger_path, contract, route_ids)
    _validate_cumulative_costs(matrix, routes)
    _validate_public_costs(contract_path, routes, cost_information, matrix)
    policy_id, decisions = _load_actions(action_path, contract_path, contract)
    expected = int(contract["expected_query_count"])
    if len(matrix) != expected or len(decisions) != expected:
        raise ScoreError("任务、ledger 与动作文件的查询数必须一致")
    decision_ids = [row["query_uid"] for row in decisions]
    if len(decision_ids) != len(set(decision_ids)):
        raise ScoreError("动作文件包含重复的 query_uid")
    if set(decision_ids) != set(matrix):
        raise ScoreError("动作文件中的查询集合与 evaluator ledger 不一致")
    unknown = sorted(
        {row["selected_route_id"] for row in decisions} - set(route_ids)
    )
    if unknown:
        raise ScoreError(f"选择了未注册的路线：{unknown}")
    return contract, routes, matrix, policy_id, decisions


def _query_rows(
    contract: dict[str, Any],
    routes: list[dict[str, Any]],
    matrix: dict[str, dict[str, tuple[float, float]]],
    decisions: list[dict[str, str]],
    lambda_value: float,
) -> list[dict[str, Any]]:
    route_ids = [route["route_id"] for route in routes]
    rank = {route_id: index for index, route_id in enumerate(route_ids)}
    fixed_route = contract["development_selected_fixed_route"]
    rows: list[dict[str, Any]] = []
    for decision in decisions:
        query_uid = decision["query_uid"]
        selected_route = decision["selected_route_id"]
        outcomes = matrix[query_uid]
        cheapest_route = min(
            route_ids, key=lambda route_id: (outcomes[route_id][1], rank[route_id])
        )
        cheapest_effectiveness, cheapest_cost = outcomes[cheapest_route]
        cheapest_utility = cheapest_effectiveness - lambda_value * cheapest_cost
        candidates = []
        for route_id in route_ids:
            effectiveness, cost = outcomes[route_id]
            utility = effectiveness - lambda_value * cost
            candidates.append((utility, -cost, -rank[route_id], route_id))
        oracle_utility, _, _, oracle_route = max(candidates)
        oracle_effectiveness, oracle_cost = outcomes[oracle_route]
        selected_effectiveness, selected_cost = outcomes[selected_route]
        selected_utility = selected_effectiveness - lambda_value * selected_cost
        fixed_effectiveness, fixed_cost = outcomes[fixed_route]
        fixed_utility = fixed_effectiveness - lambda_value * fixed_cost

        paid_routes = [
            route_id
            for route_id in route_ids
            if outcomes[route_id][1] > cheapest_cost + 1e-12
        ]
        if not paid_routes or max(
            outcomes[route_id][0] for route_id in paid_routes
        ) <= cheapest_effectiveness + 1e-12:
            stratum = "no_paid_effectiveness_gain"
        elif max(
            outcomes[route_id][0] - lambda_value * outcomes[route_id][1]
            for route_id in paid_routes
        ) <= cheapest_utility + 1e-12:
            stratum = "effectiveness_gain_rejected_by_cost"
        else:
            stratum = "paid_route_worthwhile"

        rows.append(
            {
                "query_uid": query_uid,
                "selected_route_id": selected_route,
                "selected_effectiveness": selected_effectiveness,
                "selected_cost": selected_cost,
                "selected_utility": selected_utility,
                "development_fixed_route_id": fixed_route,
                "development_fixed_effectiveness": fixed_effectiveness,
                "development_fixed_cost": fixed_cost,
                "development_fixed_utility": fixed_utility,
                "delta_utility_vs_development_fixed": selected_utility
                - fixed_utility,
                "oracle_route_id": oracle_route,
                "oracle_effectiveness": oracle_effectiveness,
                "oracle_cost": oracle_cost,
                "oracle_utility": oracle_utility,
                "regret": max(oracle_utility - selected_utility, 0.0),
                "least_cost_route_id": cheapest_route,
                "opportunity_stratum": stratum,
            }
        )
    return rows


def per_query_analysis(
    task_dir: Path,
    action_path: Path | None = None,
    lambda_value: float | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """返回一组冻结动作对应的 evaluator 专用逐查询记录。"""

    contract, routes, matrix, policy_id, decisions = _load_task(
        task_dir, action_path
    )
    lam = (
        float(lambda_value)
        if lambda_value is not None
        else float(contract["cost_profile"]["lambda"])
    )
    if lam < 0:
        raise ScoreError("lambda 必须为非负数")
    rows = _query_rows(contract, routes, matrix, decisions, lam)
    return (
        {
            "task_id": contract["task_id"],
            "policy_id": policy_id,
            "lambda": lam,
            "queries": len(rows),
            "scope": "evaluator_only",
            "interpretation": "descriptive",
        },
        rows,
    )


def sensitivity_analysis(
    task_dir: Path,
    lambda_grid: list[float],
    action_path: Path | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """在已声明或显式提供的 lambda 网格上评估冻结动作。"""

    contract, routes, matrix, policy_id, decisions = _load_task(
        task_dir, action_path
    )
    if not lambda_grid or any(value < 0 for value in lambda_grid):
        raise ScoreError("lambda 网格必须包含非负数值")
    rows: list[dict[str, Any]] = []
    for lam in lambda_grid:
        query_rows = _query_rows(contract, routes, matrix, decisions, lam)
        n = len(query_rows)
        rows.append(
            {
                "lambda": lam,
                "policy_id": policy_id,
                "mean_effectiveness": sum(
                    row["selected_effectiveness"] for row in query_rows
                )
                / n,
                "mean_cost": sum(row["selected_cost"] for row in query_rows) / n,
                "mean_utility": sum(
                    row["selected_utility"] for row in query_rows
                )
                / n,
                "development_fixed_mean_utility": sum(
                    row["development_fixed_utility"] for row in query_rows
                )
                / n,
                "delta_utility_vs_development_fixed": sum(
                    row["delta_utility_vs_development_fixed"]
                    for row in query_rows
                )
                / n,
                "oracle_mean_utility": sum(
                    row["oracle_utility"] for row in query_rows
                )
                / n,
                "mean_regret": sum(row["regret"] for row in query_rows) / n,
            }
        )
    return (
        {
            "task_id": contract["task_id"],
            "policy_id": policy_id,
            "scope": "evaluator_only",
            "interpretation": "descriptive",
        },
        rows,
    )


def budget_analysis(
    task_dir: Path,
    budget_grid: list[float],
    action_path: Path | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """汇总逐查询硬成本上限下可达到的有效性。"""

    contract, routes, matrix, policy_id, decisions = _load_task(
        task_dir, action_path
    )
    if not budget_grid or any(value < 0 for value in budget_grid):
        raise ScoreError("成本上限网格必须包含非负数值")
    route_ids = [route["route_id"] for route in routes]
    rank = {route_id: index for index, route_id in enumerate(route_ids)}
    fixed_route = contract["development_selected_fixed_route"]
    selected_by_query = {
        row["query_uid"]: row["selected_route_id"] for row in decisions
    }
    rows: list[dict[str, Any]] = []
    for budget in budget_grid:
        oracle_effectiveness: list[float] = []
        oracle_cost: list[float] = []
        selected_effectiveness: list[float] = []
        selected_feasible = 0
        fixed_feasible = 0
        for query_uid, outcomes in matrix.items():
            feasible = [
                route_id
                for route_id in route_ids
                if outcomes[route_id][1] <= budget + 1e-12
            ]
            if feasible:
                best = max(
                    feasible,
                    key=lambda route_id: (
                        outcomes[route_id][0],
                        -outcomes[route_id][1],
                        -rank[route_id],
                    ),
                )
                oracle_effectiveness.append(outcomes[best][0])
                oracle_cost.append(outcomes[best][1])
            selected = selected_by_query[query_uid]
            if outcomes[selected][1] <= budget + 1e-12:
                selected_feasible += 1
                selected_effectiveness.append(outcomes[selected][0])
            if outcomes[fixed_route][1] <= budget + 1e-12:
                fixed_feasible += 1
        n = len(matrix)
        rows.append(
            {
                "budget": budget,
                "queries": n,
                "queries_with_feasible_route": len(oracle_effectiveness),
                "budget_oracle_mean_effectiveness": (
                    sum(oracle_effectiveness) / len(oracle_effectiveness)
                    if oracle_effectiveness
                    else None
                ),
                "budget_oracle_mean_cost": (
                    sum(oracle_cost) / len(oracle_cost) if oracle_cost else None
                ),
                "policy_feasible_share": selected_feasible / n,
                "policy_mean_effectiveness_when_feasible": (
                    sum(selected_effectiveness) / len(selected_effectiveness)
                    if selected_effectiveness
                    else None
                ),
                "development_fixed_feasible_share": fixed_feasible / n,
            }
        )
    return (
        {
            "task_id": contract["task_id"],
            "policy_id": policy_id,
            "scope": "evaluator_only",
            "interpretation": "descriptive",
        },
        rows,
    )


def fixed_route_points(task_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """返回固定路线的聚合点及其 Pareto 成员关系。"""

    contract, routes, matrix, _, _ = _load_task(task_dir)
    points: list[dict[str, Any]] = []
    for route in routes:
        route_id = route["route_id"]
        effectiveness = [outcomes[route_id][0] for outcomes in matrix.values()]
        costs = [outcomes[route_id][1] for outcomes in matrix.values()]
        points.append(
            {
                "route_id": route_id,
                "route_label": route["label"],
                "mean_effectiveness": sum(effectiveness) / len(effectiveness),
                "mean_cost": sum(costs) / len(costs),
            }
        )
    for point in points:
        point["pareto"] = not any(
            other["mean_cost"] <= point["mean_cost"]
            and other["mean_effectiveness"] >= point["mean_effectiveness"]
            and (
                other["mean_cost"] < point["mean_cost"]
                or other["mean_effectiveness"] > point["mean_effectiveness"]
            )
            for other in points
        )
    return (
        {
            "task_id": contract["task_id"],
            "metric": contract["metric"]["name"],
            "scope": "evaluator_only",
            "interpretation": "descriptive",
        },
        points,
    )

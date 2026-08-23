"""Standard-library WorthIR action validation and complete-route-set scoring."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


class ScoreError(RuntimeError):
    """Raised when a contract, action file, or evaluator ledger is invalid."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScoreError(f"cannot read JSON {path.name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ScoreError(f"{path.name} must contain one JSON object")
    return payload


def _exact_fields(obj: dict[str, Any], fields: list[str], where: str) -> None:
    if set(obj) != set(fields):
        missing = sorted(set(fields) - set(obj))
        extra = sorted(set(obj) - set(fields))
        raise ScoreError(f"{where} field mismatch; missing={missing}, extra={extra}")


def _load_registry(
    contract_path: Path, contract: dict[str, Any]
) -> tuple[str, list[dict[str, Any]]]:
    registry_name = contract.get("route_registry")
    if not isinstance(registry_name, str) or not registry_name:
        raise ScoreError("contract route_registry path is malformed")
    registry_path = contract_path.parent / registry_name
    if not registry_path.is_file():
        raise ScoreError("route registry is missing")
    registry = read_json(registry_path)
    registry_id = registry.get("registry_id")
    if not isinstance(registry_id, str) or not registry_id:
        raise ScoreError("route registry must define a nonempty registry_id")
    routes = registry.get("routes")
    if not isinstance(routes, list) or not routes:
        raise ScoreError("route registry must contain a nonempty routes list")
    route_ids: list[str] = []
    normalized: list[dict[str, Any]] = []
    prerequisites: dict[str, list[str]] = {}
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            raise ScoreError(f"route {index} has an invalid schema")
        fields = set(route)
        if fields == {"route_id", "label", "parent_route_id"}:
            parent = route["parent_route_id"]
            route_prerequisites = [] if parent is None else [parent]
        elif fields == {"route_id", "label", "prerequisites"}:
            route_prerequisites = route["prerequisites"]
            if not isinstance(route_prerequisites, list) or any(
                not isinstance(value, str) or not value
                for value in route_prerequisites
            ):
                raise ScoreError(
                    f"route {index} prerequisites must be a list of route IDs"
                )
            if len(route_prerequisites) != len(set(route_prerequisites)):
                raise ScoreError(f"route {index} repeats a prerequisite")
        else:
            raise ScoreError(f"route {index} has an invalid schema")
        route_id = route["route_id"]
        if not isinstance(route_id, str) or not route_id:
            raise ScoreError(f"route {index} has an invalid route_id")
        if not isinstance(route["label"], str) or not route["label"]:
            raise ScoreError(f"route {index} has an invalid label")
        if route_id in prerequisites:
            raise ScoreError(f"duplicate route_id: {route_id}")
        route_ids.append(route_id)
        prerequisites[route_id] = list(route_prerequisites)
        normalized.append(
            {
                "route_id": route_id,
                "label": route["label"],
                "prerequisites": list(route_prerequisites),
            }
        )
    route_set = set(route_ids)
    for route_id, required_routes in prerequisites.items():
        unknown = sorted(set(required_routes) - route_set)
        if unknown:
            raise ScoreError(
                f"route {route_id} has unknown prerequisites: {unknown}"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(route_id: str) -> None:
        if route_id in visiting:
            raise ScoreError("route registry contains a prerequisite cycle")
        if route_id in visited:
            return
        visiting.add(route_id)
        for prerequisite in prerequisites[route_id]:
            visit(prerequisite)
        visiting.remove(route_id)
        visited.add(route_id)

    for route_id in route_ids:
        visit(route_id)
    return registry_id, normalized


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
        raise ScoreError("contract action schema is malformed")
    _exact_fields(actions, top_fields, "action file")
    if actions["schema_version"] != schema.get("schema_version"):
        raise ScoreError("action schema version mismatch")
    if actions["contract_id"] != contract.get("contract_id"):
        raise ScoreError("action contract_id mismatch")
    if not isinstance(actions["policy_id"], str) or not actions["policy_id"]:
        raise ScoreError("policy_id must be a nonempty string")
    decisions = actions["decisions"]
    if not isinstance(decisions, list):
        raise ScoreError("decisions must be a list")
    normalized: list[dict[str, str]] = []
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            raise ScoreError(f"decision {index} must be an object")
        _exact_fields(decision, decision_fields, f"decision {index}")
        query_uid = decision["query_uid"]
        route_id = decision["selected_route_id"]
        if not isinstance(query_uid, str) or not query_uid:
            raise ScoreError(f"decision {index} has an invalid query_uid")
        if not isinstance(route_id, str) or not route_id:
            raise ScoreError(f"decision {index} has an invalid selected_route_id")
        normalized.append({"query_uid": query_uid, "selected_route_id": route_id})
    return actions["policy_id"], normalized


def _load_ledger(
    ledger_path: Path,
    contract: dict[str, Any],
    route_ids: list[str],
) -> dict[str, dict[str, tuple[float, float]]]:
    expected_columns = contract.get("ledger_schema", {}).get("columns")
    if not isinstance(expected_columns, list):
        raise ScoreError("contract ledger schema is malformed")
    try:
        with ledger_path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != expected_columns:
                raise ScoreError(
                    f"ledger columns must be exactly {expected_columns}, "
                    f"found {reader.fieldnames}"
                )
            rows = list(reader)
    except OSError as exc:
        raise ScoreError(f"cannot read evaluator ledger: {exc}") from exc
    matrix: dict[str, dict[str, tuple[float, float]]] = {}
    metric = contract["metric"]
    q_min = float(metric["minimum"])
    q_max = float(metric["maximum"])
    for index, row in enumerate(rows):
        query_uid = row["query_uid"]
        route_id = row["route_id"]
        if not query_uid or route_id not in route_ids:
            raise ScoreError(f"ledger row {index} has an invalid key")
        try:
            effectiveness = float(row["effectiveness"])
            cost = float(row["cost"])
        except ValueError as exc:
            raise ScoreError(f"ledger row {index} has a nonnumeric value") from exc
        if not math.isfinite(effectiveness) or not math.isfinite(cost):
            raise ScoreError(f"ledger row {index} contains a non-finite value")
        if effectiveness < q_min or effectiveness > q_max:
            raise ScoreError(f"ledger row {index} effectiveness is out of range")
        if cost < 0:
            raise ScoreError(f"ledger row {index} has negative cost")
        by_route = matrix.setdefault(query_uid, {})
        if route_id in by_route:
            raise ScoreError(f"duplicate ledger key: {query_uid}/{route_id}")
        by_route[route_id] = (effectiveness, cost)
    required_routes = set(route_ids)
    for query_uid, by_route in matrix.items():
        if set(by_route) != required_routes:
            missing = sorted(required_routes - set(by_route))
            extra = sorted(set(by_route) - required_routes)
            raise ScoreError(
                f"incomplete route set for query {query_uid}; "
                f"missing={missing}, extra={extra}"
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
                        f"noncumulative cost for {query_uid}: {route_id} "
                        f"is cheaper than prerequisite {prerequisite}"
                    )


def inspect_task(
    contract_path: Path,
    ledger_path: Path,
    legal_state_path: Path | None = None,
) -> dict[str, Any]:
    """Validate a task before scoring and return a compact inventory."""

    contract_path = contract_path.resolve()
    ledger_path = ledger_path.resolve()
    contract = read_json(contract_path)
    registry_id, routes = _load_registry(contract_path, contract)
    route_ids = [route["route_id"] for route in routes]
    matrix = _load_ledger(ledger_path, contract, route_ids)
    _validate_cumulative_costs(matrix, routes)
    expected_count = int(contract["expected_query_count"])
    if len(matrix) != expected_count:
        raise ScoreError(
            f"ledger query count mismatch: expected {expected_count}, "
            f"found {len(matrix)}"
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
            raise ScoreError(f"cannot read participant legal state: {exc}") from exc
        if not legal_fields or legal_fields[0] != "query_uid":
            raise ScoreError("participant legal state must start with query_uid")
        legal_ids = [row["query_uid"] for row in rows]
        if len(legal_ids) != len(set(legal_ids)):
            raise ScoreError("participant legal state repeats query_uid values")
        if set(legal_ids) != set(matrix):
            missing = sorted(set(matrix) - set(legal_ids))
            extra = sorted(set(legal_ids) - set(matrix))
            raise ScoreError(
                f"participant legal state membership mismatch; "
                f"missing={missing}, extra={extra}"
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
    registry_id, routes = _load_registry(contract_path, contract)
    route_ids = [route["route_id"] for route in routes]
    route_rank = {route_id: index for index, route_id in enumerate(route_ids)}
    fixed_reference = contract.get("development_selected_fixed_route")
    if fixed_reference not in route_rank:
        raise ScoreError(
            "development_selected_fixed_route must name a registered route"
        )
    policy_id, decisions = _load_actions(action_path, contract_path, contract)
    matrix = _load_ledger(ledger_path, contract, route_ids)
    _validate_cumulative_costs(matrix, routes)

    expected_count = int(contract["expected_query_count"])
    if len(matrix) != expected_count:
        raise ScoreError(
            f"ledger query count mismatch: expected {expected_count}, found {len(matrix)}"
        )
    if len(decisions) != expected_count:
        raise ScoreError(
            f"action count mismatch: expected {expected_count}, found {len(decisions)}"
        )
    decision_ids = [row["query_uid"] for row in decisions]
    if len(set(decision_ids)) != len(decision_ids):
        raise ScoreError("duplicate query_uid in action file")
    if set(decision_ids) != set(matrix):
        missing = sorted(set(matrix) - set(decision_ids))
        extra = sorted(set(decision_ids) - set(matrix))
        raise ScoreError(f"action membership mismatch; missing={missing}, extra={extra}")
    unknown_routes = sorted(
        {row["selected_route_id"] for row in decisions} - set(route_ids)
    )
    if unknown_routes:
        raise ScoreError(f"unregistered selected routes: {unknown_routes}")

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
            raise ScoreError("negative regret indicates inconsistent arithmetic")
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

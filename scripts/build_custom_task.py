#!/usr/bin/env python3
"""Build a WorthIR task from generic query, route, and outcome tables."""

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
except ImportError:  # Direct script execution.
    from launcher import launcher_command


ROOT = Path(__file__).resolve().parents[1]


class BuildError(RuntimeError):
    """Raised when generic source files do not define a valid task."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot read {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"{path.name} must contain one JSON object")
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
        raise BuildError(f"cannot read {path.name}: {exc}") from exc
    if not fields:
        raise BuildError(f"{path.name} has no header")
    return fields, rows


def _number(text: str, where: str) -> float:
    try:
        value = float(text)
    except ValueError as exc:
        raise BuildError(f"{where} must be numeric") from exc
    if not math.isfinite(value):
        raise BuildError(f"{where} must be finite")
    return value


def _required_object(config: dict[str, Any], name: str) -> dict[str, Any]:
    value = config.get(name)
    if not isinstance(value, dict):
        raise BuildError(f"task.json must define an object named {name}")
    return value


def _optional_grid(config: dict[str, Any], name: str) -> list[float] | None:
    value = config.get(name)
    if value is None:
        return None
    if not isinstance(value, list) or not value:
        raise BuildError(f"cost_profile.{name} must be a nonempty numeric list")
    grid = [_number(str(item), f"cost_profile.{name}") for item in value]
    if any(item < 0 for item in grid) or len(grid) != len(set(grid)):
        raise BuildError(
            f"cost_profile.{name} must contain distinct nonnegative values"
        )
    return grid


def _read_queries(source: Path) -> tuple[list[str], list[dict[str, str]], list[str]]:
    fields, rows = _read_csv(source / "queries.csv")
    if fields[0] != "query_uid":
        raise BuildError("queries.csv must start with query_uid")
    query_ids = [row["query_uid"].strip() for row in rows]
    if not query_ids or any(not value for value in query_ids):
        raise BuildError("queries.csv must contain nonempty query_uid values")
    if len(query_ids) != len(set(query_ids)):
        raise BuildError("queries.csv repeats a query_uid")
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
            "routes.csv columns must be route_id, label, prerequisites, "
            "development_selected, and exactly one of cost or incremental_cost"
        )
    has_cost = "cost" in fields
    has_incremental = "incremental_cost" in fields
    if has_cost == has_incremental:
        raise BuildError("routes.csv must include exactly one route cost column")

    route_ids = [row["route_id"].strip() for row in rows]
    if not route_ids or any(not value for value in route_ids):
        raise BuildError("routes.csv must contain nonempty route_id values")
    if len(route_ids) != len(set(route_ids)):
        raise BuildError("routes.csv repeats a route_id")
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
            raise BuildError(f"routes.csv row {line} makes a route require itself")
        if unknown:
            raise BuildError(f"routes.csv row {line} has unknown prerequisites: {unknown}")
        value = _number(row[cost_field], f"routes.csv row {line} {cost_field}")
        if value < 0:
            raise BuildError(f"routes.csv row {line} has a negative cost")
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
        raise BuildError("routes.csv must mark exactly one development_selected route")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(route_id: str) -> None:
        if route_id in visiting:
            raise BuildError("route prerequisites contain a cycle")
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
            "outcomes.csv must contain query_uid, route_id, effectiveness, "
            "and optionally cost or incremental_cost"
        )
    outcome_cost_fields = [name for name in ("cost", "incremental_cost") if name in fields]
    if len(outcome_cost_fields) > 1:
        raise BuildError("outcomes.csv cannot contain both cost and incremental_cost")
    outcome_cost_field = outcome_cost_fields[0] if outcome_cost_fields else None
    if outcome_cost_field is not None:
        expected_route_field = "cost" if route_has_cost else "incremental_cost"
        if outcome_cost_field != expected_route_field:
            raise BuildError(
                "routes.csv and outcomes.csv must use the same cost mode"
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
            raise BuildError(f"outcomes.csv row {line} has an unknown query or route")
        if key in effectiveness:
            raise BuildError(f"outcomes.csv row {line} repeats a query-route pair")
        value = _number(row["effectiveness"], f"outcomes.csv row {line} effectiveness")
        if not metric_minimum <= value <= metric_maximum:
            raise BuildError(f"outcomes.csv row {line} effectiveness is out of range")
        effectiveness[key] = value
        if outcome_cost_field is not None:
            cost = _number(row[outcome_cost_field], f"outcomes.csv row {line} cost")
            if cost < 0:
                raise BuildError(f"outcomes.csv row {line} has a negative cost")
            per_query_values[key] = cost
    if set(effectiveness) != expected_keys:
        missing = len(expected_keys - set(effectiveness))
        extra = len(set(effectiveness) - expected_keys)
        raise BuildError(
            f"outcomes.csv must contain every query-route pair; missing={missing}, extra={extra}"
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
                        f"cumulative cost of {route_id} is below prerequisite "
                        f"{prerequisite} for query {query_uid}"
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
        raise BuildError("policy_choices.csv columns must be query_uid, selected_route_id")
    ids = [row["query_uid"].strip() for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(query_ids):
        raise BuildError("policy_choices.csv must contain each query exactly once")
    unknown = sorted({row["selected_route_id"].strip() for row in rows} - route_ids)
    if unknown:
        raise BuildError(f"policy_choices.csv selects unknown routes: {unknown}")
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
        raise BuildError(f"source directory does not exist: {source}")
    if output.exists():
        raise BuildError(f"output already exists: {output}")
    config = _read_json(source / "task.json")
    task_id = config.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise BuildError("task.json must define a nonempty task_id")
    metric = _required_object(config, "metric")
    cost_profile = _required_object(config, "cost_profile")
    metric_name = metric.get("name")
    if not isinstance(metric_name, str) or not metric_name.strip():
        raise BuildError("metric.name must be nonempty")
    minimum = _number(str(metric.get("minimum")), "metric.minimum")
    maximum = _number(str(metric.get("maximum")), "metric.maximum")
    if minimum >= maximum:
        raise BuildError("metric.minimum must be below metric.maximum")
    if metric.get("higher_is_better", True) is not True:
        raise BuildError("WorthIR currently expects a higher-is-better effectiveness measure")
    lam = _number(str(cost_profile.get("lambda")), "cost_profile.lambda")
    if lam < 0:
        raise BuildError("cost_profile.lambda must be nonnegative")
    profile_id = cost_profile.get("profile_id")
    provenance = cost_profile.get("provenance")
    availability = cost_profile.get("availability", "known_at_commitment")
    lambda_grid = _optional_grid(cost_profile, "lambda_grid")
    budget_grid = _optional_grid(cost_profile, "budget_grid")
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise BuildError("cost_profile.profile_id must be nonempty")
    if not isinstance(provenance, str) or not provenance.strip():
        raise BuildError("cost_profile.provenance must be nonempty")
    if availability not in {"known_at_commitment", "measured_after_execution"}:
        raise BuildError(
            "cost_profile.availability must be known_at_commitment or "
            "measured_after_execution"
        )

    legal_fields, legal_rows, query_ids = _read_queries(source)
    routes, prerequisites, fixed_route = _read_routes(source)
    configured_fixed = config.get("development_selected_fixed_route", fixed_route)
    if configured_fixed != fixed_route:
        raise BuildError(
            "task.json and routes.csv disagree on development_selected_fixed_route"
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
            **({"lambda_grid": lambda_grid} if lambda_grid is not None else {}),
            **({"budget_grid": budget_grid} if budget_grid is not None else {}),
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
        "score.json\ncomparison.csv\ncomparison.json\nfixed_routes.csv\norganizer_private/\n", encoding="utf-8"
    )
    try:
        task_argument = output.relative_to(ROOT).as_posix()
    except ValueError:
        task_argument = "<path-to-this-task>"
    if route_costs_file is not None:
        cost_note = (
            "Query-dependent public costs are in "
            "`participant/route_costs.csv`.\n\n"
        )
    elif availability == "known_at_commitment":
        cost_note = "Fixed public costs are in `contracts/route_registry.json`.\n\n"
    else:
        cost_note = "Costs are evaluator measurements made after execution.\n\n"
    powershell_launcher = launcher_command(ROOT, "powershell")
    posix_launcher = launcher_command(ROOT, "posix")
    (output / "README.md").write_text(
        f"# {task_id}\n\n"
        f"Cost availability: `{availability}`. {cost_note}"
        f"Validate the complete task before scoring:\n\n"
        f"```powershell\n{powershell_launcher} validate-task {task_argument}\n```\n\n"
        f"```bash\n{posix_launcher} validate-task {task_argument}\n```\n\n"
        f"Then compare the default policy with every fixed route:\n\n"
        f"```powershell\n{powershell_launcher} compare {task_argument}\n```\n\n"
        f"```bash\n{posix_launcher} compare {task_argument}\n```\n\n"
        f"Task organizers can also run `analyze`, `sensitivity`, `budget`, and "
        f"`plot`; evaluator-only outputs are written under `organizer_private/`.\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source", type=Path, help="directory containing task.json and three CSV files"
    )
    parser.add_argument("output", type=Path, help="new WorthIR task directory")
    parser.add_argument(
        "--policy-id", default="provided-policy", help="name for policy_choices.csv"
    )
    args = parser.parse_args()
    try:
        output = build_task(args.source, args.output, args.policy_id.strip())
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(f"BUILT: {output}")


if __name__ == "__main__":
    main()

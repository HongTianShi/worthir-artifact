#!/usr/bin/env python3
"""Build a runnable WorthIR task from qrels, TREC runs, and route costs."""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuildError(RuntimeError):
    """Raised when source retrieval files cannot define a valid task."""


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _read_qrels(path: Path) -> dict[str, dict[str, float]]:
    qrels: dict[str, dict[str, float]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise BuildError(f"cannot read qrels: {exc}") from exc
    for line_number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        if len(fields) == 4:
            query_uid, _, doc_id, relevance_text = fields
        elif len(fields) == 3:
            query_uid, doc_id, relevance_text = fields
        else:
            raise BuildError(
                f"qrels line {line_number} must have 3 or 4 whitespace-separated fields"
            )
        try:
            relevance = float(relevance_text)
        except ValueError as exc:
            raise BuildError(f"qrels line {line_number} has invalid relevance") from exc
        if not math.isfinite(relevance):
            raise BuildError(f"qrels line {line_number} has non-finite relevance")
        qrels.setdefault(query_uid, {})[doc_id] = relevance
    if not qrels:
        raise BuildError("qrels contain no queries")
    return qrels


def _read_run(path: Path) -> dict[str, list[str]]:
    ranked: dict[str, list[tuple[int, int, str]]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise BuildError(f"cannot read run {path}: {exc}") from exc
    for line_number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 6:
            raise BuildError(
                f"{path.name} line {line_number} must be a six-column TREC run row"
            )
        query_uid, _, doc_id, rank_text, _, _ = fields
        try:
            rank = int(rank_text)
        except ValueError as exc:
            raise BuildError(f"{path.name} line {line_number} has invalid rank") from exc
        if rank < 1:
            raise BuildError(f"{path.name} line {line_number} has nonpositive rank")
        ranked.setdefault(query_uid, []).append((rank, line_number, doc_id))
    result: dict[str, list[str]] = {}
    for query_uid, rows in ranked.items():
        rows.sort()
        seen: set[str] = set()
        result[query_uid] = []
        for _, _, doc_id in rows:
            if doc_id not in seen:
                seen.add(doc_id)
                result[query_uid].append(doc_id)
    return result


def _ndcg(relevances: dict[str, float], ranking: list[str], depth: int) -> float:
    def dcg(values: list[float]) -> float:
        return sum(
            (2.0**value - 1.0) / math.log2(index + 2)
            for index, value in enumerate(values[:depth])
        )

    observed = [max(relevances.get(doc_id, 0.0), 0.0) for doc_id in ranking]
    ideal = sorted((max(value, 0.0) for value in relevances.values()), reverse=True)
    denominator = dcg(ideal)
    return dcg(observed) / denominator if denominator else 0.0


def _read_routes(source: Path) -> list[dict[str, str]]:
    path = source / "routes.csv"
    required = [
        "route_id",
        "label",
        "parent_route_id",
        "run_file",
        "cost",
        "development_selected",
    ]
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != required:
                raise BuildError(
                    f"routes.csv columns must be exactly: {', '.join(required)}"
                )
            routes = list(reader)
    except OSError as exc:
        raise BuildError(f"cannot read routes.csv: {exc}") from exc
    if not routes:
        raise BuildError("routes.csv contains no routes")
    route_ids = [row["route_id"].strip() for row in routes]
    if any(not route_id for route_id in route_ids) or len(set(route_ids)) != len(route_ids):
        raise BuildError("route_id values must be nonempty and unique")
    selected = [
        row for row in routes if row["development_selected"].strip().lower() in {"1", "true", "yes"}
    ]
    if len(selected) != 1:
        raise BuildError("routes.csv must mark exactly one development_selected route")
    for row in routes:
        parent = row["parent_route_id"].strip()
        if parent and parent not in route_ids:
            raise BuildError(f"unknown parent route: {parent}")
        run_path = (source / row["run_file"]).resolve()
        if not run_path.is_file():
            raise BuildError(f"run file is missing: {row['run_file']}")
        try:
            cost = float(row["cost"])
        except ValueError as exc:
            raise BuildError(f"invalid cost for route {row['route_id']}") from exc
        if not math.isfinite(cost) or cost < 0:
            raise BuildError(f"cost must be nonnegative for route {row['route_id']}")
    return routes


def _read_cost_overrides(source: Path, query_ids: list[str], route_ids: list[str]) -> dict[tuple[str, str], float]:
    path = source / "costs.csv"
    if not path.is_file():
        return {}
    expected = ["query_uid", "route_id", "cost"]
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != expected:
            raise BuildError("costs.csv columns must be exactly: query_uid, route_id, cost")
        rows = list(reader)
    costs: dict[tuple[str, str], float] = {}
    for index, row in enumerate(rows, 2):
        key = (row["query_uid"], row["route_id"])
        if key[0] not in query_ids or key[1] not in route_ids:
            raise BuildError(f"costs.csv row {index} has an unknown query or route")
        try:
            cost = float(row["cost"])
        except ValueError as exc:
            raise BuildError(f"costs.csv row {index} has invalid cost") from exc
        if not math.isfinite(cost) or cost < 0 or key in costs:
            raise BuildError(f"costs.csv row {index} is invalid or duplicated")
        costs[key] = cost
    expected_keys = {(query_uid, route_id) for query_uid in query_ids for route_id in route_ids}
    if set(costs) != expected_keys:
        raise BuildError("costs.csv must contain every query-route pair when supplied")
    return costs


def _read_legal_state(
    source: Path, query_ids: list[str]
) -> tuple[list[str], list[dict[str, str]]]:
    queries = source / "queries.csv"
    if not queries.is_file():
        return ["query_uid"], [
            {"query_uid": query_uid} for query_uid in query_ids
        ]
    with queries.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or reader.fieldnames[0] != "query_uid":
            raise BuildError("queries.csv must start with a query_uid column")
        rows = list(reader)
        fields = reader.fieldnames
    ids = [row["query_uid"] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(query_ids):
        raise BuildError("queries.csv must contain each qrels query exactly once")
    return fields, rows


def _validate_route_graph_and_costs(
    routes: list[dict[str, str]],
    query_ids: list[str],
    overrides: dict[tuple[str, str], float],
) -> None:
    parents = {
        row["route_id"].strip(): row["parent_route_id"].strip() or None
        for row in routes
    }
    constants = {row["route_id"].strip(): float(row["cost"]) for row in routes}
    for route_id in parents:
        seen = {route_id}
        cursor = parents[route_id]
        while cursor is not None:
            if cursor in seen:
                raise BuildError("route parent relationships contain a cycle")
            seen.add(cursor)
            cursor = parents[cursor]
    for query_uid in query_ids:
        for route_id, parent in parents.items():
            if parent is None:
                continue
            child_cost = overrides.get((query_uid, route_id), constants[route_id])
            parent_cost = overrides.get((query_uid, parent), constants[parent])
            if child_cost < parent_cost:
                raise BuildError(
                    f"route {route_id} costs less than parent {parent} for query {query_uid}"
                )


def _read_policy(
    source: Path,
    query_ids: list[str],
    default_route: str,
    policy_id: str,
) -> tuple[str, list[dict[str, str]]]:
    path = source / "policy_choices.csv"
    if not path.is_file():
        return "development-selected-fixed", [
            {"query_uid": query_uid, "selected_route_id": default_route}
            for query_uid in query_ids
        ]
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["query_uid", "selected_route_id"]:
            raise BuildError(
                "policy_choices.csv columns must be exactly: query_uid, selected_route_id"
            )
        rows = list(reader)
    ids = [row["query_uid"] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(query_ids):
        raise BuildError("policy_choices.csv must contain each qrels query exactly once")
    return policy_id, rows


def build_task(
    source: Path,
    output: Path,
    task_id: str,
    metric: str,
    lam: float,
    policy_id: str = "provided-policy",
) -> Path:
    source = source.resolve()
    output = output.resolve()
    if not task_id:
        raise BuildError("task_id must be nonempty")
    if not policy_id:
        raise BuildError("policy_id must be nonempty")
    if output.exists():
        raise BuildError(f"output already exists: {output}")
    if not source.is_dir():
        raise BuildError(f"source directory does not exist: {source}")
    if not math.isfinite(lam) or lam < 0:
        raise BuildError("lambda must be a nonnegative number")
    metric_text = metric.strip().lower()
    if not metric_text.startswith("ndcg@"):
        raise BuildError("the built-in TREC adapter currently supports ndcg@K")
    try:
        depth = int(metric_text.split("@", 1)[1])
    except ValueError as exc:
        raise BuildError("metric must have the form ndcg@K") from exc
    if depth < 1:
        raise BuildError("NDCG depth must be positive")

    qrels = _read_qrels(source / "qrels.tsv")
    query_ids = sorted(qrels)
    routes = _read_routes(source)
    route_ids = [row["route_id"].strip() for row in routes]
    fixed_reference = next(
        row["route_id"].strip()
        for row in routes
        if row["development_selected"].strip().lower() in {"1", "true", "yes"}
    )
    overrides = _read_cost_overrides(source, query_ids, route_ids)
    _validate_route_graph_and_costs(routes, query_ids, overrides)
    run_by_route = {
        row["route_id"].strip(): _read_run(source / row["run_file"])
        for row in routes
    }
    legal_fields, legal_rows = _read_legal_state(source, query_ids)
    policy_id, decisions = _read_policy(
        source, query_ids, fixed_reference, policy_id
    )
    if any(row["selected_route_id"] not in route_ids for row in decisions):
        raise BuildError("policy_choices.csv selects an unknown route")

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

    registry = {
        "schema_version": "worthir-route-registry-v1.0",
        "registry_id": f"{task_id}-routes-v1",
        "routes": [
            {
                "route_id": row["route_id"].strip(),
                "label": row["label"].strip() or row["route_id"].strip(),
                "parent_route_id": row["parent_route_id"].strip() or None,
            }
            for row in routes
        ],
    }
    contract_id = f"{task_id}-contract-v1"
    contract = {
        "schema_version": "worthir-contract-v1.0",
        "contract_id": contract_id,
        "task_id": task_id,
        "expected_query_count": len(query_ids),
        "route_registry": "route_registry.json",
        "development_selected_fixed_route": fixed_reference,
        "action_schema": {
            "schema_version": "worthir-action-file-v1.0",
            "top_level_fields": ["schema_version", "contract_id", "policy_id", "decisions"],
            "decision_fields": ["query_uid", "selected_route_id"],
        },
        "ledger_schema": {
            "columns": ["query_uid", "route_id", "effectiveness", "cost"]
        },
        "metric": {"name": metric_text.replace("@", "_at_"), "minimum": 0.0, "maximum": 1.0},
        "cost_profile": {
            "profile_id": f"{task_id}-cost-v1",
            "provenance": "per-query costs.csv" if overrides else "declared route costs",
            "lambda": lam,
        },
    }
    _write_json(output / "contracts" / "route_registry.json", registry)
    _write_json(output / "contracts" / "task_contract.json", contract)

    with (output / "evaluator" / "ledger.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["query_uid", "route_id", "effectiveness", "cost"])
        for query_uid in query_ids:
            for row in routes:
                route_id = row["route_id"].strip()
                effectiveness = _ndcg(qrels[query_uid], run_by_route[route_id].get(query_uid, []), depth)
                cost = overrides.get((query_uid, route_id), float(row["cost"]))
                writer.writerow([query_uid, route_id, f"{effectiveness:.12g}", f"{cost:.12g}"])

    _write_json(
        output / "participant" / "actions.json",
        {
            "schema_version": "worthir-action-file-v1.0",
            "contract_id": contract_id,
            "policy_id": policy_id,
            "decisions": decisions,
        },
    )
    shutil.copy2(source / "qrels.tsv", output / "evaluator" / "qrels.tsv")
    (output / ".gitignore").write_text("score.json\ncomparison.*\nfixed_routes.csv\n", encoding="utf-8")
    try:
        task_argument = output.relative_to(ROOT).as_posix()
    except ValueError:
        task_argument = "<path-to-this-task>"
    (output / "README.md").write_text(
        f"# {task_id}\n\nBuilt from standard TREC runs and qrels.\n\n"
        f"From the WorthIR repository root, compare its routing policies with "
        f"the fixed routes:\n\n"
        f"```powershell\n.\\worthir.cmd compare {task_argument}\n```\n\n"
        f"```bash\n./worthir compare {task_argument}\n```\n\n"
        f"If the task directory is moved, replace `{task_argument}` with its new path.\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="directory containing qrels.tsv and routes.csv")
    parser.add_argument("output", type=Path, help="new WorthIR task directory")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--metric", default="ndcg@10")
    parser.add_argument("--lambda", dest="lam", type=float, default=0.08)
    parser.add_argument(
        "--policy-id",
        default="provided-policy",
        help="name for policy_choices.csv when that file is present",
    )
    args = parser.parse_args()
    try:
        output = build_task(
            args.source,
            args.output,
            args.task_id.strip(),
            args.metric,
            args.lam,
            args.policy_id.strip(),
        )
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(f"BUILT: {output}")


if __name__ == "__main__":
    main()

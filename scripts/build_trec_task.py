#!/usr/bin/env python3
"""根据 qrels、TREC run 和路线成本构建可运行的 WorthIR 任务。"""

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
    """源检索文件不能定义有效任务时抛出。"""


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _read_qrels(path: Path) -> dict[str, dict[str, float]]:
    qrels: dict[str, dict[str, float]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise BuildError(f"无法读取 qrels：{exc}") from exc
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
                f"qrels 第 {line_number} 行必须包含 3 或 4 个以空白分隔的字段"
            )
        try:
            relevance = float(relevance_text)
        except ValueError as exc:
            raise BuildError(f"qrels 第 {line_number} 行的相关性值无效") from exc
        if not math.isfinite(relevance):
            raise BuildError(f"qrels 第 {line_number} 行的相关性值不是有限数")
        qrels.setdefault(query_uid, {})[doc_id] = relevance
    if not qrels:
        raise BuildError("qrels 中没有查询")
    return qrels


def _read_run(path: Path) -> dict[str, list[str]]:
    ranked: dict[str, list[tuple[int, int, str]]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise BuildError(f"无法读取 run {path}：{exc}") from exc
    for line_number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 6:
            raise BuildError(
                f"{path.name} 第 {line_number} 行必须是六列 TREC run"
            )
        query_uid, _, doc_id, rank_text, _, _ = fields
        try:
            rank = int(rank_text)
        except ValueError as exc:
            raise BuildError(f"{path.name} 第 {line_number} 行的 rank 无效") from exc
        if rank < 1:
            raise BuildError(f"{path.name} 第 {line_number} 行的 rank 必须为正数")
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
        "prerequisites",
        "run_file",
        "cost",
        "development_selected",
    ]
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != required:
                raise BuildError(
                    f"routes.csv 必须且只能包含以下列：{', '.join(required)}"
                )
            routes = list(reader)
    except OSError as exc:
        raise BuildError(f"无法读取 routes.csv：{exc}") from exc
    if not routes:
        raise BuildError("routes.csv 中没有路线")
    route_ids = [row["route_id"].strip() for row in routes]
    if any(not route_id for route_id in route_ids) or len(set(route_ids)) != len(route_ids):
        raise BuildError("route_id 必须非空且互不重复")
    selected = [
        row for row in routes if row["development_selected"].strip().lower() in {"1", "true", "yes"}
    ]
    if len(selected) != 1:
        raise BuildError("routes.csv 必须且只能标记一条 development_selected 路线")
    for row in routes:
        prerequisites = [
            value.strip()
            for value in row["prerequisites"].split(";")
            if value.strip()
        ]
        unknown = sorted(set(prerequisites) - set(route_ids))
        if row["route_id"].strip() in prerequisites:
            raise BuildError(f"路线 {row['route_id']} 不能依赖自身")
        if len(prerequisites) != len(set(prerequisites)):
            raise BuildError(f"路线 {row['route_id']} 重复声明了前置路线")
        if unknown:
            raise BuildError(f"路线 {row['route_id']} 含有未知前置路线：{unknown}")
        run_path = (source / row["run_file"]).resolve()
        if not run_path.is_file():
            raise BuildError(f"缺少 run 文件：{row['run_file']}")
        try:
            cost = float(row["cost"])
        except ValueError as exc:
            raise BuildError(f"路线 {row['route_id']} 的成本无效") from exc
        if not math.isfinite(cost) or cost < 0:
            raise BuildError(f"路线 {row['route_id']} 的成本不得为负")
    return routes


def _read_cost_overrides(source: Path, query_ids: list[str], route_ids: list[str]) -> dict[tuple[str, str], float]:
    path = source / "costs.csv"
    if not path.is_file():
        return {}
    expected = ["query_uid", "route_id", "cost"]
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != expected:
            raise BuildError("costs.csv 必须且只能包含以下列：query_uid, route_id, cost")
        rows = list(reader)
    costs: dict[tuple[str, str], float] = {}
    for index, row in enumerate(rows, 2):
        key = (row["query_uid"], row["route_id"])
        if key[0] not in query_ids or key[1] not in route_ids:
            raise BuildError(f"costs.csv 第 {index} 行包含未知查询或路线")
        try:
            cost = float(row["cost"])
        except ValueError as exc:
            raise BuildError(f"costs.csv 第 {index} 行的成本无效") from exc
        if not math.isfinite(cost) or cost < 0 or key in costs:
            raise BuildError(f"costs.csv 第 {index} 行无效或重复")
        costs[key] = cost
    expected_keys = {(query_uid, route_id) for query_uid in query_ids for route_id in route_ids}
    if set(costs) != expected_keys:
        raise BuildError("提供 costs.csv 时必须包含每个“查询--路线”组合")
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
            raise BuildError("queries.csv 的第一列必须是 query_uid")
        rows = list(reader)
        fields = reader.fieldnames
    ids = [row["query_uid"] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(query_ids):
        raise BuildError("queries.csv 必须包含每个 qrels 查询且每个只出现一次")
    return fields, rows


def _validate_route_graph_and_costs(
    routes: list[dict[str, str]],
    query_ids: list[str],
    overrides: dict[tuple[str, str], float],
) -> None:
    prerequisites = {
        row["route_id"].strip(): [
            value.strip()
            for value in row["prerequisites"].split(";")
            if value.strip()
        ]
        for row in routes
    }
    constants = {row["route_id"].strip(): float(row["cost"]) for row in routes}
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

    for route_id in prerequisites:
        visit(route_id)
    for query_uid in query_ids:
        for route_id, required_routes in prerequisites.items():
            child_cost = overrides.get((query_uid, route_id), constants[route_id])
            for prerequisite in required_routes:
                prerequisite_cost = overrides.get(
                    (query_uid, prerequisite), constants[prerequisite]
                )
                if child_cost < prerequisite_cost:
                    raise BuildError(
                        f"查询 {query_uid} 的路线 {route_id} 成本低于"
                        f"前置路线 {prerequisite}"
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
                "policy_choices.csv 必须且只能包含以下列：query_uid, selected_route_id"
            )
        rows = list(reader)
    ids = [row["query_uid"] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(query_ids):
        raise BuildError("policy_choices.csv 必须包含每个 qrels 查询且每个只出现一次")
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
        raise BuildError("task_id 不能为空")
    if not policy_id:
        raise BuildError("policy_id 不能为空")
    if output.exists():
        raise BuildError(f"输出目录已经存在：{output}")
    if not source.is_dir():
        raise BuildError(f"源目录不存在：{source}")
    if not math.isfinite(lam) or lam < 0:
        raise BuildError("lambda 必须是非负数")
    metric_text = metric.strip().lower()
    if not metric_text.startswith("ndcg@"):
        raise BuildError("内置 TREC 适配器目前只支持 ndcg@K")
    try:
        depth = int(metric_text.split("@", 1)[1])
    except ValueError as exc:
        raise BuildError("metric 必须采用 ndcg@K 格式") from exc
    if depth < 1:
        raise BuildError("NDCG 深度必须为正数")

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
        raise BuildError("policy_choices.csv 选择了未知路线")

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
        "schema_version": "worthir-route-registry-v1.1",
        "registry_id": f"{task_id}-routes-v1",
        "routes": [
            {
                "route_id": row["route_id"].strip(),
                "label": row["label"].strip() or row["route_id"].strip(),
                "prerequisites": [
                    value.strip()
                    for value in row["prerequisites"].split(";")
                    if value.strip()
                ],
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
        f"# {task_id}\n\n根据标准 TREC run 和 qrels 构建。\n\n"
        f"从 WorthIR 仓库根目录运行以下命令，将路由策略与固定路线比较：\n\n"
        f"```powershell\n.\\worthir.cmd compare {task_argument}\n```\n\n"
        f"```bash\n./worthir compare {task_argument}\n```\n\n"
        f"如果移动了任务目录，请将 `{task_argument}` 替换为新的路径。\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="包含 qrels.tsv 和 routes.csv 的目录")
    parser.add_argument("output", type=Path, help="新的 WorthIR 任务目录")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--metric", default="ndcg@10")
    parser.add_argument("--lambda", dest="lam", type=float, default=0.08)
    parser.add_argument(
        "--policy-id",
        default="provided-policy",
        help="提供 policy_choices.csv 时为该策略指定名称",
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
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(f"已构建：{output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""比较任务策略与固定路线，并写出便于阅读的报告。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from worthir_eval import ScoreError, load_and_score  # noqa: E402


class CompareError(RuntimeError):
    """Raised when a task cannot be compared."""


def _fixed_action(contract: dict[str, Any], policy_id: str, route_id: str, query_ids: list[str]) -> dict[str, Any]:
    return {
        "schema_version": contract["action_schema"]["schema_version"],
        "contract_id": contract["contract_id"],
        "policy_id": policy_id,
        "decisions": [
            {"query_uid": query_uid, "selected_route_id": route_id}
            for query_uid in query_ids
        ],
    }


def _pareto(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        row["pareto"] = not any(
            other["mean_cost"] <= row["mean_cost"]
            and other["mean_effectiveness"] >= row["mean_effectiveness"]
            and (
                other["mean_cost"] < row["mean_cost"]
                or other["mean_effectiveness"] > row["mean_effectiveness"]
            )
            for other in rows
        )


def compare(task: Path, output_dir: Path | None = None) -> dict[str, Path]:
    task = task.resolve()
    output_dir = (output_dir or task).resolve()
    contract_path = task / "contracts" / "task_contract.json"
    registry_path = task / "contracts" / "route_registry.json"
    ledger_path = task / "evaluator" / "ledger.csv"
    default_action = task / "participant" / "actions.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompareError(f"无法读取任务定义：{exc}") from exc
    routes = registry.get("routes", [])
    if not routes:
        raise CompareError("路线注册表中没有路线")
    try:
        with ledger_path.open("r", encoding="utf-8", newline="") as stream:
            query_ids = sorted({row["query_uid"] for row in csv.DictReader(stream)})
    except OSError as exc:
        raise CompareError(f"无法读取评测 ledger：{exc}") from exc
    action_paths = [default_action] if default_action.is_file() else []
    policies_dir = task / "participant" / "policies"
    if policies_dir.is_dir():
        action_paths.extend(sorted(policies_dir.glob("*.json")))
    scores: list[dict[str, Any]] = []
    seen_policy_ids: set[str] = set()
    try:
        for action_path in action_paths:
            score = load_and_score(contract_path, ledger_path, action_path)
            if score["policy_id"] in seen_policy_ids:
                raise CompareError(f"policy_id 重复：{score['policy_id']}")
            seen_policy_ids.add(score["policy_id"])
            score["kind"] = "routing policy"
            scores.append(score)
        with tempfile.TemporaryDirectory(prefix="worthir-fixed-") as temp:
            for index, route in enumerate(routes):
                policy_id = f"fixed:{route['route_id']}"
                if policy_id in seen_policy_ids:
                    raise CompareError(
                        f"policy_id {policy_id!r} 保留给固定路线报告使用"
                    )
                action_path = Path(temp) / f"fixed-{index:04d}.json"
                action_path.write_text(
                    json.dumps(
                        _fixed_action(contract, policy_id, route["route_id"], query_ids)
                    ),
                    encoding="utf-8",
                )
                score = load_and_score(contract_path, ledger_path, action_path)
                score["kind"] = "fixed route"
                score["route_id"] = route["route_id"]
                score["route_label"] = route["label"]
                scores.append(score)
    except ScoreError as exc:
        raise CompareError(str(exc)) from exc

    fixed_reference = contract["development_selected_fixed_route"]
    reference = next(row for row in scores if row.get("route_id") == fixed_reference)
    fixed_rows = [row for row in scores if row["kind"] == "fixed route"]
    _pareto(fixed_rows)
    for row in scores:
        row["delta_utility_vs_development_fixed"] = round(
            row["mean_utility"] - reference["mean_utility"], 12
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    comparison_json = output_dir / "comparison.json"
    comparison_csv = output_dir / "comparison.csv"
    fixed_csv = output_dir / "fixed_routes.csv"
    report_md = output_dir / "comparison.md"
    comparison_json.write_text(
        json.dumps(
            {
                "task_id": contract["task_id"],
                "development_selected_fixed_route": fixed_reference,
                "rows": scores,
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    fields = [
        "policy_id",
        "kind",
        "queries",
        "mean_effectiveness",
        "mean_cost",
        "mean_utility",
        "delta_utility_vs_development_fixed",
        "mean_exact_within_route_set_regret",
        "oracle_match_share",
    ]
    with comparison_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(scores)
    with fixed_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "route_id",
                "route_label",
                "mean_effectiveness",
                "mean_cost",
                "mean_utility",
                "pareto",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(fixed_rows)

    lines = [
        f"# WorthIR 比较：{contract['task_id']}",
        "",
        f"开发集选定的固定路线：`{fixed_reference}`。",
        "以下数值是该任务全部查询上的描述性均值。",
        "",
        "| 策略 | 类型 | 有效性 | 成本 | 效用 | 相对固定路线的 Delta U | 遗憾 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in scores:
        display_kind = "路由策略" if row["kind"] == "routing policy" else "固定路线"
        lines.append(
            "| {policy_id} | {kind} | {mean_effectiveness:.4f} | {mean_cost:.4f} | "
            "{mean_utility:.4f} | {delta_utility_vs_development_fixed:+.4f} | "
            "{mean_exact_within_route_set_regret:.4f} |".format(
                **{**row, "kind": display_kind}
            )
        )
    lines.extend(
        [
            "",
            "`fixed_routes.csv` 标记固定路线中不受支配的有效性--成本 Pareto 曲线。",
            "该描述性报告不作任何不确定性声明。",
            "",
        ]
    )
    report_md.write_text("\n".join(lines), encoding="utf-8")
    return {
        "comparison_json": comparison_json,
        "comparison_csv": comparison_csv,
        "fixed_routes_csv": fixed_csv,
        "report": report_md,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    try:
        outputs = compare(args.task_dir, args.output_dir)
    except CompareError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(
        json.dumps(
            {key: str(value) for key, value in outputs.items()},
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

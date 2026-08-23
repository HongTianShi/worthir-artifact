#!/usr/bin/env python3
"""校验完整 WorthIR 任务并汇总其内容。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from worthir_eval import ScoreError, inspect_task  # noqa: E402


def validate(task: Path) -> dict:
    task = task.resolve()
    return inspect_task(
        task / "contracts" / "task_contract.json",
        task / "evaluator" / "ledger.csv",
        task / "participant" / "legal_state.csv",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path, help="WorthIR 任务目录")
    parser.add_argument(
        "--output", type=Path, help="可选的 JSON 校验摘要"
    )
    args = parser.parse_args()
    try:
        summary = validate(args.task_dir)
    except (ScoreError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    metric = summary["metric"]["name"]
    cost_mode = "随查询变化" if summary["query_dependent_cost"] else "按路线固定"
    print(
        "任务有效\n"
        f"  任务：{summary['task_id']}\n"
        f"  查询数：{summary['queries']}\n"
        f"  路线数：{summary['routes']}\n"
        f"  查询--路线结果数：{summary['query_route_rows']}\n"
        f"  有效性指标：{metric}\n"
        f"  成本模式：{cost_mode}\n"
        f"  成本可见时点：{summary['cost_availability']}\n"
        f"  公开成本来源：{summary['public_cost_source']}\n"
        f"  前置关系边数：{summary['prerequisite_edges']}\n"
        f"  固定参考路线：{summary['development_selected_fixed_route']}"
    )


if __name__ == "__main__":
    main()

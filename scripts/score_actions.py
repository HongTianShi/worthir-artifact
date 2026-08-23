#!/usr/bin/env python3
"""使用完整评测 ledger 对严格的 WorthIR 动作文件评分。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from worthir_eval import ScoreError, load_and_score  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task-dir",
        type=Path,
        help="使用标准 contracts/participant/evaluator 任务布局",
    )
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--actions", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.task_dir:
        if args.contract or args.ledger:
            parser.error("--task-dir 不能与 --contract 或 --ledger 同时使用")
        task = args.task_dir.resolve()
        contract = task / "contracts" / "task_contract.json"
        ledger = task / "evaluator" / "ledger.csv"
        actions = (
            args.actions.resolve()
            if args.actions
            else task / "participant" / "actions.json"
        )
        output = args.output.resolve() if args.output else task / "score.json"
    else:
        missing = [
            name
            for name, value in {
                "--contract": args.contract,
                "--ledger": args.ledger,
                "--actions": args.actions,
                "--output": args.output,
            }.items()
            if value is None
        ]
        if missing:
            parser.error("缺少必要参数：" + ", ".join(missing))
        contract = args.contract
        ledger = args.ledger
        actions = args.actions
        output = args.output
    try:
        result = load_and_score(contract, ledger, actions)
    except ScoreError as exc:
        print(f"已拒绝：{exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "queries": result["queries"],
                "mean_effectiveness": result["mean_effectiveness"],
                "mean_cost": result["mean_cost"],
                "mean_utility": result["mean_utility"],
                "mean_regret": result["mean_exact_within_route_set_regret"],
                "output": str(output),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

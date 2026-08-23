#!/usr/bin/env python3
"""连接上游检索流程与 WorthIR CSV 的任务适配器模板。"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    raise SystemExit(
        "这是任务适配器边界，并未内置大型检索流程。请按照任务说明，用该任务的路线运行程序替换工作目录中的 "
        f"{Path(__file__).name}。程序必须向 --output 写出 task.json、queries.csv、routes.csv 与 outcomes.csv；"
        "在 20 查询 smoke 中遵守 --limit；并且绝不能使用评价结果选择路线。"
    )


if __name__ == "__main__":
    main()

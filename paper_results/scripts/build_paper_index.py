#!/usr/bin/env python3
"""验证 PAPER_SPEC.json 并生成复算结果总索引。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_MAIN = {
    *(f"figure{number}" for number in range(1, 8)),
    *(f"table{number}" for number in range(1, 7)),
}
EXPECTED_APPENDIX = {
    "appendix_table_a1",
    "appendix_table_a2",
    "appendix_table_b1",
    "appendix_table_b2",
    "appendix_table_c1",
    "appendix_table_d1",
    "appendix_table_d2",
    *(f"appendix_table_e{number}" for number in range(1, 7)),
    "appendix_figure_e1",
    "appendix_figure_e2",
    "appendix_figure_f1",
    "appendix_figure_f2",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--paper-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    main_items = spec["main_items"]
    appendix_items = spec["appendix_items"]
    main_ids = {item["id"] for item in main_items}
    appendix_ids = {item["id"] for item in appendix_items}
    if main_ids != EXPECTED_MAIN:
        raise RuntimeError(
            f"正文映射不一致：缺少={sorted(EXPECTED_MAIN - main_ids)}，"
            f"多出={sorted(main_ids - EXPECTED_MAIN)}"
        )
    if appendix_ids != EXPECTED_APPENDIX:
        raise RuntimeError(
            f"附录映射不一致：缺少={sorted(EXPECTED_APPENDIX - appendix_ids)}，"
            f"多出={sorted(appendix_ids - EXPECTED_APPENDIX)}"
        )
    all_items = main_items + appendix_items
    outputs = [item["output"] for item in all_items]
    if len(outputs) != len(set(outputs)):
        raise RuntimeError("PAPER_SPEC.json 中存在重复输出文件名")
    missing = [name for name in outputs if not (args.paper_root / name).is_file()]
    if missing:
        raise RuntimeError(f"缺少论文输出：{missing}")

    paper = spec["paper"]
    lines = [
        "# 论文复算结果",
        "",
        f"**论文：** {paper['title']}",
        "",
        f"**论文版本：** {paper['version']}",
        "",
        f"**Artifact 版本：** [{paper['artifact_release']}]({paper['artifact_release_url']})",
        "",
        "本次运行已生成或检查下列全部文件。",
        "",
        "## 正文",
        "",
        "| 项目 | 状态 | 复现层级 | 输出 |",
        "| --- | --- | --- | --- |",
    ]
    for item in main_items:
        lines.append(
            f"| {item['id'].replace('figure', 'Figure ').replace('table', 'Table ')} "
            f"| PASS | {item['level']} | [{item['output']}](paper/{item['output']}) |"
        )
    lines.extend(
        [
            "",
            "## 附录",
            "",
            "| 项目 | 状态 | 复现层级 | 输出 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in appendix_items:
        label = item["id"].replace("appendix_", "Appendix ").replace("_", " ")
        lines.append(
            f"| {label} | PASS | {item['level']} | "
            f"[{item['output']}](paper/{item['output']}) |"
        )
    lines.extend(
        [
            "",
            "## Captions",
            "",
        ]
    )
    for item in all_items:
        lines.extend([f"### {item['id']}", "", item["caption"], ""])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "PASS", "items": len(all_items)}))


if __name__ == "__main__":
    main()

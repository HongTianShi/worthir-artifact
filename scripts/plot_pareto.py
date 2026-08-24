#!/usr/bin/env python3
"""绘制无额外依赖的固定路线与策略有效性—成本 SVG。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from worthir_eval import ScoreError, fixed_route_points, per_query_analysis  # noqa: E402

try:
    from .organizer_io import output_path
except ImportError:
    from organizer_io import output_path


def _scale(value: float, low: float, high: float, start: float, end: float) -> float:
    if high <= low:
        return (start + end) / 2
    return start + (value - low) * (end - start) / (high - low)


def draw(task: Path, actions: Path | None, destination: Path) -> None:
    metadata, points = fixed_route_points(task)
    policy_metadata, query_rows = per_query_analysis(task, actions)
    policy = {
        "mean_cost": sum(row["selected_cost"] for row in query_rows) / len(query_rows),
        "mean_effectiveness": sum(row["selected_effectiveness"] for row in query_rows) / len(query_rows),
        "policy_id": policy_metadata["policy_id"],
    }
    all_costs = [point["mean_cost"] for point in points] + [policy["mean_cost"]]
    all_effectiveness = [point["mean_effectiveness"] for point in points] + [policy["mean_effectiveness"]]
    cost_pad = max(max(all_costs) - min(all_costs), 1.0) * 0.08
    eff_pad = max(max(all_effectiveness) - min(all_effectiveness), 0.1) * 0.12
    x_low, x_high = min(all_costs) - cost_pad, max(all_costs) + cost_pad
    y_low, y_high = min(all_effectiveness) - eff_pad, max(all_effectiveness) + eff_pad
    left, right, top, bottom = 110.0, 940.0, 95.0, 560.0
    x = lambda value: _scale(value, x_low, x_high, left, right)
    y = lambda value: _scale(value, y_low, y_high, bottom, top)
    pareto = sorted((point for point in points if point["pareto"]), key=lambda row: row["mean_cost"])
    curve = " ".join(f"{x(point['mean_cost']):.1f},{y(point['mean_effectiveness']):.1f}" for point in pareto)
    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650" viewBox="0 0 1000 650">',
        '<rect width="1000" height="650" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:24px;font-weight:700}.sub{font-size:14px;fill:#52606d}.axis{stroke:#17212b;stroke-width:2}.grid{stroke:#dbe3ea;stroke-width:1}.route{fill:#2878b5;stroke:white;stroke-width:2}.policy{fill:#d97706;stroke:#17212b;stroke-width:2}.label{font-size:14px}.tick{font-size:12px;fill:#52606d}</style>',
        f'<text x="110" y="38" class="title">有效性—成本 Pareto 曲线：{escape(metadata["task_id"])}</text>',
        '<text x="110" y="64" class="sub">描述性 evaluator 专用结果；蓝色表示固定路线，橙色表示冻结的路由策略。</text>',
    ]
    for index in range(6):
        xv = x_low + (x_high - x_low) * index / 5
        xp = x(xv)
        elements.extend([
            f'<line x1="{xp:.1f}" y1="{top}" x2="{xp:.1f}" y2="{bottom}" class="grid"/>',
            f'<text x="{xp:.1f}" y="585" text-anchor="middle" class="tick">{xv:.3g}</text>',
        ])
        yv = y_low + (y_high - y_low) * index / 5
        yp = y(yv)
        elements.extend([
            f'<line x1="{left}" y1="{yp:.1f}" x2="{right}" y2="{yp:.1f}" class="grid"/>',
            f'<text x="96" y="{yp + 4:.1f}" text-anchor="end" class="tick">{yv:.3g}</text>',
        ])
    elements.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis"/>',
        '<text x="525" y="625" text-anchor="middle" class="label">平均累计成本</text>',
        f'<text x="28" y="330" text-anchor="middle" class="label" transform="rotate(-90 28 330)">平均 {escape(metadata["metric"])}</text>',
    ])
    if len(pareto) > 1:
        elements.append(f'<polyline points="{curve}" fill="none" stroke="#16527a" stroke-width="3"/>')
    for point in points:
        xp, yp = x(point["mean_cost"]), y(point["mean_effectiveness"])
        elements.extend([
            f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="7" class="route"/>',
            f'<text x="{xp + 10:.1f}" y="{yp - 10:.1f}" class="label">{escape(point["route_label"])}</text>',
        ])
    xp, yp = x(policy["mean_cost"]), y(policy["mean_effectiveness"])
    diamond = f"{xp:.1f},{yp-10:.1f} {xp+10:.1f},{yp:.1f} {xp:.1f},{yp+10:.1f} {xp-10:.1f},{yp:.1f}"
    elements.extend([
        f'<polygon points="{diamond}" class="policy"/>',
        f'<text x="{xp + 13:.1f}" y="{yp + 22:.1f}" class="label">{escape(policy["policy_id"])}</text>',
        '</svg>',
    ])
    destination.write_text("\n".join(elements) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path, help="WorthIR 任务目录")
    parser.add_argument("--actions", type=Path, help="冻结的动作 JSON")
    parser.add_argument("--output", type=Path, help="组织者私有 SVG 输出")
    args = parser.parse_args()
    try:
        destination = output_path(args.task_dir, args.output, "pareto.svg")
        if destination.suffix.lower() != ".svg":
            raise ValueError("绘图输出必须以 .svg 结尾")
        draw(args.task_dir, args.actions, destination)
    except (ScoreError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(json.dumps({"status": "PASS", "scope": "evaluator_only", "interpretation": "descriptive", "output": str(destination)}, indent=2))


if __name__ == "__main__":
    main()

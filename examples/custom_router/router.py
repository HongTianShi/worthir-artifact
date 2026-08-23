#!/usr/bin/env python3
"""Cost-aware router using only participant-visible task files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def public_costs(task: Path, registry: dict) -> dict[tuple[str, str], float]:
    info = registry["cost_information"]
    if info["availability"] != "known_at_commitment":
        raise ValueError("this router requires costs known at commitment time")
    if info["mode"] == "fixed":
        return {
            ("*", route["route_id"]): float(route["cost"])
            for route in registry["routes"]
        }
    path = (task / "contracts" / info["route_costs_file"]).resolve()
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return {
            (row["query_uid"], row["route_id"]): float(row["cost"])
            for row in csv.DictReader(stream)
        }


def predicted_effectiveness(row: dict[str, str], route_id: str) -> float:
    """Replace these estimates with predictions from your own router."""

    length = int(row["question_length"])
    product_code = row["contains_product_code"].lower() == "true"
    if route_id == "keyword_search":
        return 0.86 if length <= 12 and not product_code else 0.58
    if route_id == "semantic_search":
        return 0.90 if length > 20 else 0.79
    if route_id == "combined_review":
        return 0.95 if product_code else 0.87
    return 0.0


def route(task: Path, output: Path) -> Path:
    contract = read_json(task / "contracts" / "task_contract.json")
    registry = read_json(task / "contracts" / contract["route_registry"])
    costs = public_costs(task, registry)
    route_ids = [item["route_id"] for item in registry["routes"]]
    lam = float(contract["cost_profile"]["lambda"])
    with (task / "participant" / "legal_state.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))

    decisions = []
    for row in rows:
        query_uid = row["query_uid"]
        selected = max(
            route_ids,
            key=lambda route_id: (
                predicted_effectiveness(row, route_id)
                - lam * costs.get((query_uid, route_id), costs.get(("*", route_id))),
                -route_ids.index(route_id),
            ),
        )
        decisions.append({"query_uid": query_uid, "selected_route_id": selected})

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["query_uid", "selected_route_id"]
        )
        writer.writeheader()
        writer.writerows(decisions)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create cost-aware choices without reading evaluator outcomes."
    )
    parser.add_argument("task_dir", type=Path, help="built WorthIR task directory")
    parser.add_argument("output", type=Path, help="choice CSV to create")
    args = parser.parse_args()
    print(f"WROTE: {route(args.task_dir.resolve(), args.output.resolve())}")


if __name__ == "__main__":
    main()

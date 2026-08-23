#!/usr/bin/env python3
"""Score one selected TREC-DL route per topic."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).parent)
    parser.add_argument("--actions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lambda-value", type=float, default=0.08)
    args = parser.parse_args()

    root = args.root.resolve()
    action_path = args.actions
    if not action_path.is_absolute():
        action_path = root / action_path
    payload = json.loads(action_path.read_text(encoding="utf-8"))
    decisions = pd.DataFrame(payload["decisions"])
    if list(decisions.columns) != ["query_uid", "selected_route_id"]:
        raise SystemExit("actions must contain query_uid and selected_route_id")

    registry = json.loads(
        (root / "public" / "contracts" / "route_registry.json").read_text(
            encoding="utf-8"
        )
    )
    routes = [row["route_id"] for row in registry["routes"]]
    if not set(decisions["selected_route_id"]).issubset(routes):
        raise SystemExit("actions contain an unknown route")

    frames = []
    for year in ("2019", "2020"):
        frame = pd.read_parquet(
            root / "organizer_private" / "data" / "test" / year
            / "route_outcomes.parquet"
        )
        frame["year"] = year
        frames.append(frame)
    outcomes = pd.concat(frames, ignore_index=True)
    expected = set(outcomes["query_uid"])
    if len(decisions) != len(expected) or set(decisions["query_uid"]) != expected:
        raise SystemExit("actions must cover every evaluation topic exactly once")
    if decisions["query_uid"].duplicated().any():
        raise SystemExit("actions contain duplicate topics")

    selected = decisions.merge(
        outcomes,
        left_on=["query_uid", "selected_route_id"],
        right_on=["query_uid", "route_id"],
        how="left",
        validate="one_to_one",
    )
    if selected["raw_ndcg_at_10"].isna().any():
        raise SystemExit("actions could not be joined to route outcomes")

    lam = args.lambda_value
    selected["utility"] = selected["raw_ndcg_at_10"] - lam * selected["C_op"]
    candidates = outcomes.copy()
    candidates["utility"] = candidates["raw_ndcg_at_10"] - lam * candidates["C_op"]
    oracle = candidates.groupby("query_uid")["utility"].max()
    selected["regret"] = (
        selected["query_uid"].map(oracle) - selected["utility"]
    ).clip(lower=0)

    by_year = {}
    for year, rows in selected.groupby("year", sort=True):
        by_year[year] = {
            "topics": int(len(rows)),
            "mean_ndcg_at_10": float(rows["raw_ndcg_at_10"].mean()),
            "mean_cost": float(rows["C_op"].mean()),
            "mean_utility": float(rows["utility"].mean()),
            "mean_regret": float(rows["regret"].mean()),
            "action_counts": dict(Counter(rows["selected_route_id"])),
        }
    result = {
        "status": "PASS",
        "policy_id": payload.get("policy_id", "unnamed-policy"),
        "lambda": lam,
        "by_year": by_year,
    }
    output = args.output
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

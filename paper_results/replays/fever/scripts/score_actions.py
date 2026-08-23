#!/usr/bin/env python3
"""Fail-closed scorer for one WorthIR--FEVER route choice per test query."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROUTES = ("bm25", "bi200", "ce20", "ce100", "hybrid")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actions", required=True, type=Path)
    parser.add_argument("--lambda-value", type=float, default=0.08)
    parser.add_argument("--bundle-root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    actions = pd.read_csv(args.actions)
    if list(actions.columns) != ["query_uid", "selected_route"]:
        raise SystemExit("actions must contain exactly query_uid,selected_route")
    if len(actions) != 13332 or actions["query_uid"].duplicated().any():
        raise SystemExit("actions must contain exactly 13,332 unique queries")
    if not set(actions["selected_route"]).issubset(ROUTES):
        raise SystemExit("unregistered selected_route")

    private = args.bundle_root / "organizer_private"
    outcomes = pd.read_parquet(private / "test_outcomes.parquet")
    costs = pd.read_parquet(private / "route_costs.parquet")
    outcomes = outcomes[outcomes["evaluation_role"] == "official_dev_test"]
    test_ids = set(outcomes["query_uid"])
    if set(actions["query_uid"]) != test_ids:
        raise SystemExit("action membership mismatch")

    quality = outcomes.pivot(index="query_uid", columns="route", values="raw_ndcg_10")
    cost = costs[costs["query_uid"].isin(test_ids)].pivot(
        index="query_uid", columns="route", values="cost_work"
    )
    order = actions["query_uid"].tolist()
    q = quality.loc[order, list(ROUTES)].to_numpy()
    c = cost.loc[order, list(ROUTES)].to_numpy()
    if q.shape != (13332, 5) or c.shape != (13332, 5):
        raise SystemExit("incomplete hidden matrix")
    if not np.isfinite(q).all() or not np.isfinite(c).all():
        raise SystemExit("non-finite hidden matrix")

    route_index = {route: i for i, route in enumerate(ROUTES)}
    chosen = np.asarray([route_index[x] for x in actions["selected_route"]])
    utility = q - args.lambda_value * c
    rows = np.arange(len(order))
    selected_quality = q[rows, chosen]
    selected_cost = c[rows, chosen]
    selected_utility = utility[rows, chosen]
    oracle_utility = utility.max(axis=1)
    oracle = utility.argmax(axis=1)

    result = {
        "schema_version": "worthir-fever-action-score-v1.0",
        "queries": len(order),
        "lambda": args.lambda_value,
        "mean_raw_ndcg_10": float(selected_quality.mean()),
        "mean_cost_work": float(selected_cost.mean()),
        "mean_utility": float(selected_utility.mean()),
        "mean_regret": float((oracle_utility - selected_utility).mean()),
        "zero_regret_share": float(np.mean(oracle == chosen)),
        "action_share": dict(Counter(actions["selected_route"])),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()

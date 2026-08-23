#!/usr/bin/env python3
"""Fail-closed scorer for one MuSiQue WorthIR action per test query."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROUTES = ("V0", "V1", "V2", "V3")


def asset_path(root: Path, name: str, private: bool = False) -> Path:
    workspace_path = root / "assets" / name
    if workspace_path.is_file():
        return workspace_path
    bundle_group = "organizer_private" if private else "participant"
    bundle_path = root / bundle_group / name
    if bundle_path.is_file():
        return bundle_path
    raise RuntimeError(f"Missing {'private' if private else 'public'} asset: {name}")


def read_actions(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
    elif path.suffix.lower() in {".parquet", ".pq"}:
        frame = pd.read_parquet(path)
    else:
        raise RuntimeError("Action file must be CSV or Parquet")
    required = {"query_uid", "selected_route"}
    if not required.issubset(frame.columns):
        raise RuntimeError(f"Missing action columns: {sorted(required-frame.columns)}")
    return frame[["query_uid", "selected_route"]].copy()


def common_cost_table(root: Path, test_outcomes: pd.DataFrame) -> pd.DataFrame:
    report = json.loads(
        (root / "reports" / "common_denominator_cost_results.json").read_text(
            encoding="utf-8"
        )
    )
    denominator = float(
        report["cost_definition"]["development_denominator"]
    )
    legal = pd.read_parquet(asset_path(root, "legal_state.parquet"))
    legal = legal[legal["split"].eq("test")][
        [
            "query_uid",
            "n_decomposition",
            "title_token_counts",
            "paragraph_token_counts",
        ]
    ].copy()
    title = legal["title_token_counts"].map(sum).astype(np.float64)
    paragraph = (
        legal["title_token_counts"].map(sum)
        + legal["paragraph_token_counts"].map(sum)
    ).astype(np.float64)
    decomposition = legal["n_decomposition"].astype(np.float64)
    work = pd.DataFrame(
        {
            "query_uid": legal["query_uid"],
            "work_V0": 0.0,
            "work_V1": decomposition * title,
            "work_V2": paragraph,
            "work_V3": decomposition * title
            + (1.0 + decomposition) * paragraph,
        }
    ).melt(
        id_vars="query_uid",
        var_name="route",
        value_name="raw_operator_work",
    )
    work["route"] = work["route"].str.removeprefix("work_")
    result = test_outcomes.drop(
        columns=["operator_cost", "utility"]
    ).merge(work, on=["query_uid", "route"], validate="one_to_one")
    result["operator_cost"] = result["raw_operator_work"] / denominator
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--actions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--cost-profile",
        choices=["relative_v1", "common_devmean_v1"],
        default="relative_v1",
    )
    parser.add_argument("--lambda-value", type=float, default=0.08)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError(f"Refusing overwrite: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    membership = pd.read_parquet(
        asset_path(root, "query_membership.parquet")
    )
    test_ids = sorted(
        membership.loc[membership["split"].eq("test"), "query_uid"].tolist()
    )
    actions = read_actions(args.actions.resolve())
    if len(actions) != len(test_ids):
        raise RuntimeError(
            f"Expected {len(test_ids)} actions, found {len(actions)}"
        )
    if actions["query_uid"].duplicated().any():
        raise RuntimeError("Duplicate query_uid in action file")
    if set(actions["query_uid"]) != set(test_ids):
        missing = sorted(set(test_ids) - set(actions["query_uid"]))
        extra = sorted(set(actions["query_uid"]) - set(test_ids))
        raise RuntimeError(
            f"Action membership mismatch; missing={missing[:3]}, extra={extra[:3]}"
        )
    invalid = sorted(set(actions["selected_route"]) - set(ROUTES))
    if invalid:
        raise RuntimeError(f"Unregistered routes: {invalid}")

    outcomes = pd.read_parquet(
        asset_path(root, "route_outcomes_private.parquet", private=True),
        filters=[("split", "=", "test")],
    )
    if len(outcomes) != len(test_ids) * len(ROUTES):
        raise RuntimeError("Incomplete official-validation menu")
    if args.cost_profile == "common_devmean_v1":
        outcomes = common_cost_table(root, outcomes)
    outcomes["scored_utility"] = (
        outcomes["ndcg_at_4"] - args.lambda_value * outcomes["operator_cost"]
    )
    realized = actions.merge(
        outcomes,
        left_on=["query_uid", "selected_route"],
        right_on=["query_uid", "route"],
        how="left",
        validate="one_to_one",
    )
    if realized["ndcg_at_4"].isna().any():
        raise RuntimeError("Unscored action")
    oracle = (
        outcomes.sort_values(
            ["query_uid", "scored_utility", "operator_cost", "route"],
            ascending=[True, False, True, True],
        )
        .drop_duplicates("query_uid")
        .rename(
            columns={
                "route": "oracle_route",
                "scored_utility": "oracle_utility",
            }
        )[["query_uid", "oracle_route", "oracle_utility"]]
    )
    scored = realized.merge(oracle, on="query_uid", validate="one_to_one")
    scored["regret"] = scored["oracle_utility"] - scored["scored_utility"]
    result = {
        "surface": "musique-worthir-v1",
        "evidence_status": "retrospective outcome-separated",
        "queries": len(scored),
        "cost_profile": args.cost_profile,
        "lambda": args.lambda_value,
        "mean_raw_ndcg_at_4": float(scored["ndcg_at_4"].mean()),
        "mean_cost": float(scored["operator_cost"].mean()),
        "mean_utility": float(scored["scored_utility"].mean()),
        "mean_exact_within_menu_regret": float(scored["regret"].mean()),
        "zero_regret_share": float(np.isclose(scored["regret"], 0.0).mean()),
        "oracle_match_share": float(
            scored["selected_route"].eq(scored["oracle_route"]).mean()
        ),
        "action_share": {
            route: float(scored["selected_route"].eq(route).mean())
            for route in ROUTES
        },
        "information_boundary": (
            "action validated before organizer-private outcome join"
        ),
    }
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

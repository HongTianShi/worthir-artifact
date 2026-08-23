#!/usr/bin/env python3
"""Frozen-action MuSiQue cost sensitivity; no fitting or action reselection."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


LAMBDAS = [0.0, 0.02, 0.04, 0.08, 0.16, 0.32]
SEED = 20260730


def ci(values: np.ndarray) -> list[float]:
    rng = np.random.default_rng(SEED)
    means = []
    for _ in range(10000):
        indices = rng.integers(0, len(values), size=len(values))
        means.append(float(values[indices].mean()))
    return [float(value) for value in np.quantile(means, [0.025, 0.975])]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = root / "reports" / "postgate_cost_sensitivity.json"
    report = root / "reports" / "POSTGATE_COST_SENSITIVITY.md"
    if output.exists() or report.exists():
        raise RuntimeError("Sensitivity outputs exist; refusing overwrite")

    outcomes = pd.read_parquet(root / "assets" / "route_outcomes_private.parquet")
    actions = pd.read_parquet(
        root / "assets" / "official_validation_actions.parquet"
    )[["query_uid", "selected_route"]]
    rows = []
    for lam in LAMBDAS:
        frame = outcomes.copy()
        frame["u_lambda"] = frame["ndcg_at_4"] - lam * frame["operator_cost"]
        dev_means = (
            frame[frame["split"].eq("dev")]
            .groupby("route")["u_lambda"]
            .mean()
        )
        fdev_route = sorted(
            dev_means.index, key=lambda route: (-dev_means[route], route)
        )[0]
        test = frame[frame["split"].eq("test")]
        test_means = test.groupby("route")["u_lambda"].mean()
        ftih_route = sorted(
            test_means.index, key=lambda route: (-test_means[route], route)
        )[0]
        adaptive = (
            actions.merge(
                test[
                    [
                        "query_uid",
                        "route",
                        "ndcg_at_4",
                        "operator_cost",
                        "u_lambda",
                    ]
                ],
                left_on=["query_uid", "selected_route"],
                right_on=["query_uid", "route"],
                validate="one_to_one",
            )
            .set_index("query_uid")
            .sort_index()
        )
        fixed = (
            test[test["route"].eq(fdev_route)]
            .set_index("query_uid")
            .sort_index()
        )
        oracle = (
            test.pivot(index="query_uid", columns="route", values="u_lambda")
            .max(axis=1)
            .sort_index()
        )
        utility_diff = (adaptive["u_lambda"] - fixed["u_lambda"]).to_numpy()
        raw_diff = (adaptive["ndcg_at_4"] - fixed["ndcg_at_4"]).to_numpy()
        cost_diff = (
            adaptive["operator_cost"] - fixed["operator_cost"]
        ).to_numpy()
        headroom = (oracle - fixed["u_lambda"]).to_numpy()
        rows.append(
            {
                "lambda": lam,
                "F_dev": fdev_route,
                "F_TIH": ftih_route,
                "delta_utility": float(utility_diff.mean()),
                "delta_utility_ci95": ci(utility_diff),
                "delta_raw_quality": float(raw_diff.mean()),
                "delta_operator_cost": float(cost_diff.mean()),
                "recoverability": float(utility_diff.mean() / headroom.mean()),
            }
        )

    payload = {
        "analysis_id": "musique-worthir-postgate-cost-sensitivity-v1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "post-gate frozen-action sensitivity",
        "action_vector": "A_dev trained and selected only at lambda=.08",
        "rows": rows,
    }
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# MuSiQue post-gate cost sensitivity",
        "",
        "This is a frozen-action sensitivity, not a refit or a second "
        "preregistered gate. The official-validation `A_dev` action vector is "
        "unchanged; only the declared preference weight and corresponding fixed "
        "references are rescored.",
        "",
        "| lambda | F_dev | delta raw | delta cost | delta utility (95% CI) | kappa |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['lambda']:.2f} | {row['F_dev']} | "
            f"{row['delta_raw_quality']:.6f} | "
            f"{row['delta_operator_cost']:.6f} | "
            f"{row['delta_utility']:.6f} "
            f"[{row['delta_utility_ci95'][0]:.6f}, "
            f"{row['delta_utility_ci95'][1]:.6f}] | "
            f"{row['recoverability']:.2%} |"
        )
    lines += [
        "",
        "The analysis tests whether the held-out conclusion is tied to the "
        "single headline weight. It does not claim policy transfer because the "
        "action vector was development-selected at lambda=.08.",
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "lambda": LAMBDAS}))


if __name__ == "__main__":
    main()

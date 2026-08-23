#!/usr/bin/env python3
"""Cluster-stability readout for the common-denominator MuSiQue profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260730
N_BOOT = 10000


def cluster_bootstrap(
    values: np.ndarray, labels: np.ndarray, seed_offset: int
) -> list[float]:
    frame = pd.DataFrame({"value": values, "label": labels})
    grouped = frame.groupby("label")["value"].agg(["sum", "count"])
    sums = grouped["sum"].to_numpy(np.float64)
    counts = grouped["count"].to_numpy(np.float64)
    n_clusters = len(grouped)
    rng = np.random.default_rng(SEED + seed_offset)
    means = np.empty(N_BOOT, dtype=np.float64)
    cursor = 0
    while cursor < N_BOOT:
        batch = min(256, N_BOOT - cursor)
        sampled = rng.integers(
            0, n_clusters, size=(batch, n_clusters)
        )
        means[cursor : cursor + batch] = (
            sums[sampled].sum(axis=1) / counts[sampled].sum(axis=1)
        )
        cursor += batch
    return [float(value) for value in np.quantile(means, [0.025, 0.975])]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    assets = root / "assets"
    reports = root / "reports"
    output_json = reports / "common_cost_dependence_results.json"
    output_md = reports / "COMMON_COST_DEPENDENCE_AUDIT.md"
    for path in (output_json, output_md):
        if path.exists():
            raise RuntimeError(f"Refusing overwrite: {path}")

    cost_result = json.loads(
        (reports / "common_denominator_cost_results.json").read_text(
            encoding="utf-8"
        )
    )
    denominator = float(
        cost_result["cost_definition"]["development_denominator"]
    )
    actions = pd.read_parquet(
        assets / "common_denominator_actions.parquet"
    )[["query_uid", "utility_common"]].rename(
        columns={"utility_common": "adaptive_utility"}
    )
    legal = pd.read_parquet(assets / "legal_state.parquet")
    legal = legal[legal["split"].eq("test")][
        [
            "query_uid",
            "title_token_counts",
            "paragraph_token_counts",
        ]
    ].copy()
    paragraph_work = (
        legal["title_token_counts"].map(sum)
        + legal["paragraph_token_counts"].map(sum)
    ).astype(np.float64)
    legal["V2_common_cost"] = paragraph_work / denominator
    v2 = pd.read_parquet(
        assets / "route_outcomes_private.parquet",
        filters=[("split", "=", "test"), ("route", "=", "V2")],
    )[["query_uid", "ndcg_at_4"]].merge(
        legal[["query_uid", "V2_common_cost"]],
        on="query_uid",
        validate="one_to_one",
    )
    v2["fixed_utility"] = v2["ndcg_at_4"] - 0.08 * v2["V2_common_cost"]
    components = pd.read_parquet(
        assets / "official_validation_components.parquet"
    )
    scored = (
        actions.merge(
            v2[["query_uid", "fixed_utility"]],
            on="query_uid",
            validate="one_to_one",
        )
        .merge(components.drop(columns=["delta_utility"]), on="query_uid")
        .sort_values("query_uid")
    )
    scored["delta"] = scored["adaptive_utility"] - scored["fixed_utility"]
    intervals: dict[str, list[float]] = {}
    for offset, name in enumerate(
        [
            "support_title",
            "support_paragraph_text",
            "decomposition_question",
            "union",
        ],
        start=1,
    ):
        intervals[name] = cluster_bootstrap(
            scored["delta"].to_numpy(np.float64),
            scored[f"component_{name}"].to_numpy(np.int64),
            offset,
        )
    result = {
        "analysis_id": "musique-worthir-common-cost-dependence-v1.0",
        "point_estimate": float(scored["delta"].mean()),
        "lambda": 0.08,
        "F_dev": "V2",
        "intervals": intervals,
        "interpretation": (
            "conditional component-resampling stability on the fixed "
            "official-validation ledger"
        ),
    }
    output_json.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# MuSiQue common-cost dependence audit",
        "",
        f"- Exact contrast: {result['point_estimate']:.6f}.",
        "- All intervals are conditional component-resampling stability "
        "ranges on the fixed official-validation ledger.",
        "",
        "| Component | 95% range |",
        "|---|---:|",
    ]
    for name, ci in intervals.items():
        lines.append(f"| {name} | [{ci[0]:.6f},{ci[1]:.6f}] |")
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Organizer-private scorer for the WorthIR Hyperlink10k surface."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EXPECTED_SURFACE_ID = "worthir-hyperlink10k-scoring-surface-v1.0"
EXPECTED_TASK_ID = "worthir-2wiki-hyperlink10k-v1.0"
VIEW_ORDER = [
    "summary",
    "provided_context",
    "hyperlink_1hop",
    "hyperlink_2hop",
    "full_local_pool",
]
VIEW_COSTS = {
    "summary": 0.00,
    "provided_context": 0.08,
    "hyperlink_1hop": 0.20,
    "hyperlink_2hop": 0.34,
    "full_local_pool": 0.55,
}
LAMBDA = 0.08
sys.dont_write_bytecode = True


class ScoringError(RuntimeError):
    """A deterministic private-scoring failure."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScoringError(f"Cannot read valid UTF-8 JSON: {path}") from exc


def verify_layer(root: Path, expected_layer: str) -> dict[str, Any]:
    manifest = load_json(root / "manifest.json")
    if manifest.get("surface_id") != EXPECTED_SURFACE_ID:
        raise ScoringError(f"Unexpected {expected_layer} surface_id")
    if manifest.get("task_id") != EXPECTED_TASK_ID:
        raise ScoringError(f"Unexpected {expected_layer} task_id")
    if manifest.get("layer") != expected_layer:
        raise ScoringError(f"Unexpected {expected_layer} layer marker")
    return manifest


def load_public_validator(public_root: Path):
    path = public_root / "validate_submission.py"
    spec = importlib.util.spec_from_file_location(
        "worthir_hyperlink10k_public_validator", path
    )
    if spec is None or spec.loader is None:
        raise ScoringError("Cannot load public submission validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def finite_mean(values: np.ndarray, name: str) -> float:
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ScoringError(f"Invalid vector for {name}")
    return float(values.mean())


def score(
    public_root: Path,
    private_root: Path,
    submission_path: Path,
) -> dict[str, Any]:
    public_root = public_root.resolve()
    private_root = private_root.resolve()
    public_manifest = verify_layer(public_root, "participant_public")
    private_manifest = verify_layer(private_root, "organizer_private")

    validator = load_public_validator(public_root)
    try:
        submission, decisions = validator.validate_submission(
            public_root, submission_path.resolve()
        )
    except Exception as exc:
        raise ScoringError(f"Submission validation failed: {exc}") from exc

    outcomes = pd.read_parquet(private_root / "data" / "raw_outcomes.parquet")
    expected_outcome_columns = [
        "query_uid",
        "view",
        "raw_quality_ndcg_at_4",
        "support_title_recall_at_4",
        "support_title_f1_at_4",
        "triple_endpoint_recall_at_4",
        "triple_endpoint_f1_at_4",
    ]
    if list(outcomes.columns) != expected_outcome_columns:
        raise ScoringError("Unexpected private outcome schema")
    if len(outcomes) != 50_000 or outcomes[["query_uid", "view"]].duplicated().any():
        raise ScoringError("Private outcomes are not a complete 10,000 x 5 matrix")
    raw = outcomes.pivot(
        index="query_uid", columns="view", values="raw_quality_ndcg_at_4"
    )
    if set(raw.columns) != set(VIEW_ORDER) or raw.isna().any().any():
        raise ScoringError("Private outcome menu is incomplete")
    raw = raw[VIEW_ORDER]
    raw_array = raw.to_numpy(np.float64)
    if (
        not np.isfinite(raw_array).all()
        or (raw_array < 0).any()
        or (raw_array > 1).any()
    ):
        raise ScoringError("Private raw-quality values are invalid")
    costs = np.asarray([VIEW_COSTS[view] for view in VIEW_ORDER], dtype=np.float64)
    utility = raw_array - LAMBDA * costs[None, :]
    oracle_index = np.argmax(utility, axis=1)
    oracle_utility = utility[np.arange(len(raw)), oracle_index]

    row_by_uid = {uid: index for index, uid in enumerate(raw.index.astype(str))}
    try:
        row_index = np.asarray(
            [row_by_uid[uid] for uid in decisions["query_uid"]],
            dtype=np.int64,
        )
        selected_index = np.asarray(
            [VIEW_ORDER.index(view) for view in decisions["selected_view"]],
            dtype=np.int64,
        )
    except (KeyError, ValueError) as exc:
        raise ScoringError("Submission cannot align to private outcomes") from exc

    selected_raw = raw_array[row_index, selected_index]
    selected_cost = costs[selected_index]
    selected_utility = selected_raw - LAMBDA * selected_cost
    selected_oracle = oracle_utility[row_index]
    regret = np.maximum(selected_oracle - selected_utility, 0.0)
    selected_views = decisions["selected_view"].to_numpy(str)
    oracle_views = np.asarray(
        [VIEW_ORDER[index] for index in oracle_index[row_index]], dtype=str
    )

    references = pd.read_parquet(private_root / "data" / "references.parquet")
    expected_reference_columns = [
        "seed",
        "query_uid",
        "partition",
        "f_dev_view",
        "f_tih_view",
        "quality_dev_view",
    ]
    if list(references.columns) != expected_reference_columns:
        raise ScoringError("Unexpected private reference schema")
    seed = int(submission["evaluation_seed"])
    references = references.loc[references["seed"] == seed].copy()
    if len(references) != 2_001 or references["query_uid"].nunique() != 2_001:
        raise ScoringError("Private seed reference ledger is incomplete")
    references = references.set_index("query_uid").loc[decisions["query_uid"]]
    view_to_index = {view: index for index, view in enumerate(VIEW_ORDER)}

    def reference_values(column: str) -> np.ndarray:
        indices = references[column].map(view_to_index)
        if indices.isna().any():
            raise ScoringError(f"Unknown view in private reference {column}")
        return utility[row_index, indices.to_numpy(np.int64)]

    f_dev = reference_values("f_dev_view")
    f_tih = reference_values("f_tih_view")
    quality_dev = reference_values("quality_dev_view")
    delta_dev = selected_utility - f_dev
    delta_tih = selected_utility - f_tih
    headroom_dev = selected_oracle - f_dev
    headroom_tih = selected_oracle - f_tih
    paid = selected_cost > 0
    oracle_paid = oracle_views != "summary"
    summary_utility = utility[row_index, 0]

    def ratio(numerator: np.ndarray, denominator: np.ndarray) -> float | None:
        denominator_mean = finite_mean(denominator, "ratio denominator")
        if denominator_mean <= 0:
            return None
        return finite_mean(numerator, "ratio numerator") / denominator_mean

    return {
        "schema_version": "worthir-hyperlink10k-score-v1.0",
        "surface_id": EXPECTED_SURFACE_ID,
        "task_id": EXPECTED_TASK_ID,
        "policy_id": submission["policy_id"],
        "evaluation_seed": seed,
        "partition": "test",
        "decision_count": 2_001,
        "training_provenance": "unverified",
        "utility_contract": {
            "lambda": LAMBDA,
            "cost_profile": "2wiki-hyper-v1-op",
            "utility": "raw_quality - lambda * cumulative_declared_cost",
        },
        "aggregate": {
            "raw_quality_ndcg_at_4": finite_mean(selected_raw, "raw quality"),
            "declared_cost": finite_mean(selected_cost, "cost"),
            "utility": finite_mean(selected_utility, "utility"),
            "exact_within_menu_regret": finite_mean(regret, "regret"),
            "oracle_match_rate": float(np.mean(selected_views == oracle_views)),
            "action_counts": {
                view: int(np.sum(selected_views == view)) for view in VIEW_ORDER
            },
            "action_shares": {
                view: float(np.mean(selected_views == view)) for view in VIEW_ORDER
            },
        },
        "frozen_reference_comparisons": {
            "delta_vs_f_dev": finite_mean(delta_dev, "delta f_dev"),
            "delta_vs_f_tih": finite_mean(delta_tih, "delta f_tih"),
            "delta_vs_quality_dev_fixed": finite_mean(
                selected_utility - quality_dev, "delta quality fixed"
            ),
            "fixed_to_oracle_headroom_dev": finite_mean(
                headroom_dev, "headroom dev"
            ),
            "fixed_to_oracle_headroom_tih": finite_mean(
                headroom_tih, "headroom tih"
            ),
            "kappa_dev": ratio(delta_dev, headroom_dev),
            "kappa_tih": ratio(delta_tih, headroom_tih),
        },
        "purchase_error_taxonomy": {
            "unnecessary_purchase_count": int(np.sum(paid & ~oracle_paid)),
            "missed_acquisition_count": int(np.sum(~paid & oracle_paid)),
            "wrong_paid_view_count": int(
                np.sum(paid & oracle_paid & (selected_views != oracle_views))
            ),
            "harmful_purchase_vs_summary_count": int(
                np.sum(paid & (selected_utility < summary_utility - 1e-12))
            ),
        },
        "privacy": "aggregate_only_no_query_outcomes_or_oracle_actions",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = score(
            args.public_root, args.private_root, args.submission
        )
    except Exception as exc:
        print(json.dumps({"scored": False, "error": str(exc)}, sort_keys=True))
        raise SystemExit(2) from exc
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "scored": True,
                "policy_id": result["policy_id"],
                "utility": result["aggregate"]["utility"],
                "regret": result["aggregate"]["exact_within_menu_regret"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

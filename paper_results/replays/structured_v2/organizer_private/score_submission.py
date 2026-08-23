#!/usr/bin/env python
"""Organizer-private aggregate scorer for WorthIR Structured-v2."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EXPECTED_SURFACE_ID = "worthir-structured-v2-scoring-surface-v1.2"
EXPECTED_TASK_ID = "worthir-2wiki-structured-v2.0"
VIEW_ORDER = ["summary", "one_hop", "two_hop", "full_context", "ce"]
VIEW_COSTS = {
    "summary": 0.0,
    "one_hop": 0.16,
    "two_hop": 0.26,
    "full_context": 0.55,
    "ce": 0.95,
}
LAMBDA = 0.08
BOOTSTRAP_REPETITIONS = 10_000
BOOTSTRAP_SEED = 20260728
sys.dont_write_bytecode = True


class ScoringError(RuntimeError):
    """A deterministic private-scoring failure."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScoringError(f"Cannot read valid UTF-8 JSON: {path}") from exc


def verify_public_manifest(public_root: Path) -> None:
    manifest = load_json(public_root / "manifest.json")
    if manifest.get("surface_id") != EXPECTED_SURFACE_ID:
        raise ScoringError("Unexpected public surface_id")
    if manifest.get("task_id") != EXPECTED_TASK_ID:
        raise ScoringError("Unexpected public task_id")


def verify_private_manifest(private_root: Path, public_root: Path) -> None:
    manifest = load_json(private_root / "manifest.json")
    if manifest.get("surface_id") != EXPECTED_SURFACE_ID:
        raise ScoringError("Unexpected private surface_id")
    if manifest.get("task_id") != EXPECTED_TASK_ID:
        raise ScoringError("Unexpected private task_id")


def load_public_validator(public_root: Path):
    path = public_root / "validate_submission.py"
    spec = importlib.util.spec_from_file_location("worthir_public_validator", path)
    if spec is None or spec.loader is None:
        raise ScoringError("Cannot load public submission validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def component_sums_and_counts(
    values: np.ndarray, component_ids: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=np.float64)
    component_ids = np.asarray(component_ids, dtype=str)
    if (
        values.ndim != 1
        or component_ids.ndim != 1
        or values.shape != component_ids.shape
        or not np.isfinite(values).all()
        or np.any(component_ids == "")
    ):
        raise ScoringError(
            "Component-bootstrap inputs must be aligned finite vectors"
        )
    _, inverse = np.unique(component_ids, return_inverse=True)
    return (
        np.bincount(inverse, weights=values).astype(np.float64),
        np.bincount(inverse).astype(np.float64),
    )


def paired_interval(
    values: np.ndarray, component_ids: np.ndarray
) -> dict[str, float]:
    values = np.asarray(values, dtype=np.float64)
    sums, counts = component_sums_and_counts(values, component_ids)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    estimates = np.empty(BOOTSTRAP_REPETITIONS, dtype=np.float64)
    n = len(sums)
    batch = 250
    for start in range(0, BOOTSTRAP_REPETITIONS, batch):
        stop = min(start + batch, BOOTSTRAP_REPETITIONS)
        indices = rng.integers(0, n, size=(stop - start, n), dtype=np.int32)
        estimates[start:stop] = (
            sums[indices].sum(axis=1) / counts[indices].sum(axis=1)
        )
    low, high = np.quantile(estimates, [0.025, 0.975])
    return {
        "estimate": float(values.mean()),
        "ci95_low": float(low),
        "ci95_high": float(high),
    }


def ratio_interval(
    numerator: np.ndarray,
    denominator: np.ndarray,
    component_ids: np.ndarray,
) -> dict[str, float]:
    numerator = np.asarray(numerator, dtype=np.float64)
    denominator = np.asarray(denominator, dtype=np.float64)
    if (
        numerator.shape != denominator.shape
        or numerator.ndim != 1
        or not np.isfinite(numerator).all()
        or not np.isfinite(denominator).all()
    ):
        raise ScoringError("Ratio-bootstrap inputs must be aligned finite vectors")
    numerator_sums, counts = component_sums_and_counts(
        numerator, component_ids
    )
    denominator_sums, denominator_counts = component_sums_and_counts(
        denominator, component_ids
    )
    if not np.array_equal(counts, denominator_counts):
        raise ScoringError("Component counts differ across ratio inputs")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    estimates = np.empty(BOOTSTRAP_REPETITIONS, dtype=np.float64)
    n = len(numerator_sums)
    batch = 250
    for start in range(0, BOOTSTRAP_REPETITIONS, batch):
        stop = min(start + batch, BOOTSTRAP_REPETITIONS)
        indices = rng.integers(0, n, size=(stop - start, n), dtype=np.int32)
        sampled_denominator_sum = denominator_sums[indices].sum(axis=1)
        if np.any(sampled_denominator_sum <= 0):
            raise ScoringError("Non-positive bootstrap headroom")
        estimates[start:stop] = (
            numerator_sums[indices].sum(axis=1)
            / sampled_denominator_sum
        )
    estimate = float(numerator.mean() / denominator.mean())
    low, high = np.quantile(estimates, [0.025, 0.975])
    return {
        "estimate": estimate,
        "ci95_low": float(low),
        "ci95_high": float(high),
    }


def oracle_indices(utility: np.ndarray) -> np.ndarray:
    """Return first-in-contract argmax indices, including exact ties."""
    utility = np.asarray(utility, dtype=np.float64)
    if utility.ndim != 2 or utility.shape[1] != len(VIEW_ORDER):
        raise ScoringError("Oracle utility matrix has the wrong shape")
    return np.argmax(utility, axis=1)


def score(
    public_root: Path, private_root: Path, submission_path: Path
) -> dict[str, Any]:
    public_root = public_root.resolve()
    private_root = private_root.resolve()
    verify_public_manifest(public_root)
    verify_private_manifest(private_root, public_root)
    validator = load_public_validator(public_root)
    try:
        submission, decisions = validator.validate_submission(
            public_root, submission_path.resolve()
        )
    except Exception as exc:
        raise ScoringError(f"Submission validation failed: {exc}") from exc
    outcomes = pd.read_parquet(private_root / "data" / "outcomes.parquet")
    references = pd.read_parquet(private_root / "data" / "references.parquet")
    if list(outcomes.columns) != [
        "query_uid",
        "view",
        "raw_quality",
        "declared_cost",
    ]:
        raise ScoringError("Unexpected private outcome schema")
    if len(outcomes) != 10_000 or outcomes[["query_uid", "view"]].duplicated().any():
        raise ScoringError("Private outcome ledger is not a complete 2,000 x 5 matrix")
    if list(references.columns) != [
        "query_uid",
        "source_row_index",
        "component_id",
        "outer_fold",
        "dev_fold",
        "f_dev_view",
        "f_tih_view",
        "a_oof_view",
        "selected_learner",
    ]:
        raise ScoringError("Unexpected private reference schema")
    if len(references) != 2000 or references["query_uid"].nunique() != 2000:
        raise ScoringError("Private reference ledger must contain 2,000 unique queries")

    raw = outcomes.pivot(index="query_uid", columns="view", values="raw_quality")
    costs = outcomes.pivot(index="query_uid", columns="view", values="declared_cost")
    if set(raw.columns) != set(VIEW_ORDER) or raw.isna().any().any():
        raise ScoringError("Private outcome menu is incomplete")
    raw = raw[VIEW_ORDER]
    costs = costs[VIEW_ORDER]
    expected_costs = np.asarray([VIEW_COSTS[v] for v in VIEW_ORDER], dtype=np.float64)
    if not np.allclose(costs.to_numpy(float), expected_costs[None, :], atol=0, rtol=0):
        raise ScoringError("Private outcome costs do not match the frozen contract")
    raw_array = raw.to_numpy(np.float64)
    if not np.isfinite(raw_array).all() or (raw_array < 0).any() or (raw_array > 1).any():
        raise ScoringError("Private raw-quality values are invalid")
    utility = raw_array - LAMBDA * expected_costs[None, :]
    oracle_index = oracle_indices(utility)
    oracle_utility = utility[np.arange(len(raw)), oracle_index]

    index_by_uid = {uid: i for i, uid in enumerate(raw.index.astype(str))}
    try:
        selected_index = np.asarray(
            [VIEW_ORDER.index(view) for view in decisions["selected_view"]],
            dtype=np.int64,
        )
        row_index = np.asarray(
            [index_by_uid[uid] for uid in decisions["query_uid"]], dtype=np.int64
        )
    except (KeyError, ValueError) as exc:
        raise ScoringError("Validated submission cannot align to private outcomes") from exc
    selected_raw = raw_array[row_index, selected_index]
    selected_cost = expected_costs[selected_index]
    selected_utility = selected_raw - LAMBDA * selected_cost
    selected_oracle = oracle_utility[row_index]
    regret = np.maximum(selected_oracle - selected_utility, 0.0)

    refs = references.set_index("query_uid").loc[decisions["query_uid"]]
    component_ids = refs["component_id"].to_numpy(str)
    view_to_index = {view: i for i, view in enumerate(VIEW_ORDER)}

    def reference_values(column: str) -> np.ndarray:
        indices = refs[column].map(view_to_index)
        if indices.isna().any():
            raise ScoringError(f"Unknown view in private reference {column}")
        idx = indices.to_numpy(np.int64)
        return utility[row_index, idx]

    f_dev = reference_values("f_dev_view")
    f_tih = reference_values("f_tih_view")
    a_oof = reference_values("a_oof_view")
    summary_utility = utility[row_index, 0]
    delta_dev = selected_utility - f_dev
    delta_tih = selected_utility - f_tih
    delta_a = selected_utility - a_oof
    headroom_dev = selected_oracle - f_dev
    headroom_tih = selected_oracle - f_tih
    selected_views = decisions["selected_view"].to_numpy(str)
    oracle_views = np.asarray([VIEW_ORDER[i] for i in oracle_index[row_index]], dtype=str)
    paid = selected_cost > 0
    oracle_paid = oracle_views != "summary"

    mean_headroom_dev = float(headroom_dev.mean())
    mean_headroom_tih = float(headroom_tih.mean())
    result = {
        "schema_version": "worthir-structured-v2-score-v1.2",
        "surface_id": EXPECTED_SURFACE_ID,
        "task_id": EXPECTED_TASK_ID,
        "policy_id": submission["policy_id"],
        "training_provenance": "unverified",
        "decision_count": 2000,
        "utility_contract": {
            "lambda": LAMBDA,
            "cost_profile": "2wiki-structured-v2-cop-v1.0",
            "utility": "raw_quality - lambda * cumulative_declared_cost",
        },
        "aggregate": {
            "raw_quality": paired_interval(selected_raw, component_ids),
            "declared_cost": paired_interval(selected_cost, component_ids),
            "utility": paired_interval(selected_utility, component_ids),
            "exact_within_menu_regret": paired_interval(
                regret, component_ids
            ),
            "oracle_match_rate": float(np.mean(selected_views == oracle_views)),
            "action_counts": {
                view: int(np.sum(selected_views == view)) for view in VIEW_ORDER
            },
            "action_shares": {
                view: float(np.mean(selected_views == view)) for view in VIEW_ORDER
            },
        },
        "frozen_reference_comparisons": {
            "delta_vs_f_dev": paired_interval(delta_dev, component_ids),
            "delta_vs_f_tih": paired_interval(delta_tih, component_ids),
            "delta_vs_frozen_a_oof": paired_interval(
                delta_a, component_ids
            ),
            "fixed_to_oracle_headroom_dev": paired_interval(
                headroom_dev, component_ids
            ),
            "fixed_to_oracle_headroom_tih": paired_interval(
                headroom_tih, component_ids
            ),
            "kappa_dev": (
                ratio_interval(delta_dev, headroom_dev, component_ids)
                if mean_headroom_dev > 0
                else None
            ),
            "kappa_tih": (
                ratio_interval(delta_tih, headroom_tih, component_ids)
                if mean_headroom_tih > 0
                else None
            ),
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
            "definitions": {
                "unnecessary_purchase": (
                    "paid view selected when the within-menu oracle selected summary"
                ),
                "missed_acquisition": (
                    "summary selected when the within-menu oracle selected a paid view"
                ),
                "wrong_paid_view": (
                    "paid view selected that differs from the oracle paid view"
                ),
                "harmful_purchase_vs_summary": (
                    "paid view selected with lower utility than summary"
                ),
            },
        },
        "privacy": "aggregate_only_no_query_outcomes_or_oracle_actions",
        "bootstrap": {
            "unit": "support-title connected component",
            "components": int(np.unique(component_ids).size),
            "reference_note": (
                "Frozen references are support-title-component-disjoint "
                "stitched OOF procedure estimates; submission training "
                "provenance is not certified by action-vector scoring."
            ),
            "repetitions": BOOTSTRAP_REPETITIONS,
            "seed": BOOTSTRAP_SEED,
        },
    }
    return result


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
        result = score(args.public_root, args.private_root, args.submission)
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
                "utility": result["aggregate"]["utility"]["estimate"],
                "regret": result["aggregate"]["exact_within_menu_regret"]["estimate"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

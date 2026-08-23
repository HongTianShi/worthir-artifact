#!/usr/bin/env python
"""Fail-closed validator for WorthIR Hyperlink10k action submissions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


EXPECTED_SURFACE_ID = "worthir-hyperlink10k-scoring-surface-v1.0"
EXPECTED_TASK_ID = "worthir-2wiki-hyperlink10k-v1.0"
EXPECTED_SCHEMA_ID = "worthir-hyperlink10k-submission-v1.0"
EXPECTED_VIEWS = {
    "summary",
    "provided_context",
    "hyperlink_1hop",
    "hyperlink_2hop",
    "full_local_pool",
}
EXPECTED_SEEDS = {17, 23, 31, 43, 59}
ROOT_KEYS = {
    "schema_id",
    "task_id",
    "evaluation_seed",
    "partition",
    "policy_id",
    "decisions",
}
DECISION_KEYS = {"query_uid", "selected_view"}


class ValidationError(RuntimeError):
    """A deterministic participant-facing validation failure."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Cannot read valid UTF-8 JSON: {path}") from exc


def verify_manifest(root: Path) -> dict[str, Any]:
    manifest = load_json(root / "manifest.json")
    if manifest.get("surface_id") != EXPECTED_SURFACE_ID:
        raise ValidationError("Unexpected public surface_id")
    if manifest.get("task_id") != EXPECTED_TASK_ID:
        raise ValidationError("Unexpected public task_id")
    return manifest


def validate_public_data(public_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    membership = pd.read_parquet(
        public_root / "data" / "query_membership.parquet"
    )
    expected_membership = {
        "query_uid",
        "source_query_id",
        "source_row_index",
        "source_dataset",
        "source_split",
        "canonical_group_id",
        "frozen_stratum",
        "provenance_key",
    }
    if not expected_membership.issubset(membership.columns):
        raise ValidationError("Unexpected public membership schema")
    if len(membership) != 10_000 or membership["query_uid"].nunique() != 10_000:
        raise ValidationError("Public membership must contain 10,000 unique queries")
    if membership[["query_uid", "source_query_id"]].isna().any().any():
        raise ValidationError("Public membership contains null identifiers")

    splits = pd.read_parquet(public_root / "data" / "split_assignments.parquet")
    expected_split_columns = {
        "seed",
        "query_uid",
        "frozen_stratum",
        "partition",
        "target_ratio",
        "a1_partition_role",
        "a2_partition_role",
        "assignment_algorithm_version",
    }
    if not expected_split_columns.issubset(splits.columns):
        raise ValidationError("Unexpected public split schema")
    if len(splits) != 50_000 or splits[["seed", "query_uid"]].duplicated().any():
        raise ValidationError("Public split ledger must contain 50,000 unique rows")
    if set(splits["seed"].astype(int)) != EXPECTED_SEEDS:
        raise ValidationError("Public split ledger has an unexpected seed")
    expected_ids = set(membership["query_uid"].astype(str))
    for seed in sorted(EXPECTED_SEEDS):
        seed_rows = splits.loc[splits["seed"] == seed]
        if set(seed_rows["query_uid"].astype(str)) != expected_ids:
            raise ValidationError(f"Seed {seed} does not cover the public population")
        if seed_rows["partition"].value_counts().to_dict() != {
            "train": 5_999,
            "dev_or_calibration": 2_000,
            "test": 2_001,
        }:
            raise ValidationError(f"Seed {seed} has invalid partition counts")
    return membership, splits


def validate_submission(
    public_root: Path,
    submission_path: Path,
) -> tuple[dict[str, Any], pd.DataFrame]:
    public_root = public_root.resolve()
    verify_manifest(public_root)
    membership, splits = validate_public_data(public_root)
    task = load_json(public_root / "contracts" / "task_contract.json")
    route = load_json(public_root / "contracts" / "route_registry.json")
    cost = load_json(public_root / "contracts" / "cost_contract.json")

    submission = load_json(submission_path.resolve())
    if not isinstance(submission, dict):
        raise ValidationError("Submission root must be an object")
    if set(submission) != ROOT_KEYS:
        missing = sorted(ROOT_KEYS - set(submission))
        extra = sorted(set(submission) - ROOT_KEYS)
        raise ValidationError(
            f"Submission root schema mismatch; missing={missing}, extra={extra}"
        )
    if submission["schema_id"] != EXPECTED_SCHEMA_ID:
        raise ValidationError("Unexpected submission schema_id")
    if submission["task_id"] != EXPECTED_TASK_ID:
        raise ValidationError("Unexpected submission task_id")
    seed = submission["evaluation_seed"]
    if not isinstance(seed, int) or seed not in EXPECTED_SEEDS:
        raise ValidationError("Unexpected evaluation_seed")
    if submission["partition"] != "test":
        raise ValidationError("Only the frozen test partition can be scored")
    if cost.get("task_id") != EXPECTED_TASK_ID or route.get(
        "task_id"
    ) != EXPECTED_TASK_ID:
        raise ValidationError("Contract task binding mismatch")

    policy_id = submission["policy_id"]
    if (
        not isinstance(policy_id, str)
        or policy_id != policy_id.strip()
        or not (1 <= len(policy_id) <= 120)
        or any(ord(character) < 32 or ord(character) == 127 for character in policy_id)
    ):
        raise ValidationError(
            "policy_id must contain 1--120 visible characters without edge whitespace"
        )

    decisions = submission["decisions"]
    if not isinstance(decisions, list) or len(decisions) != 2_001:
        raise ValidationError("Submission must contain exactly 2,001 decisions")
    rows: list[dict[str, str]] = []
    for index, row in enumerate(decisions):
        if not isinstance(row, dict) or set(row) != DECISION_KEYS:
            raise ValidationError(
                f"Decision {index} must contain only query_uid and selected_view"
            )
        query_uid = row["query_uid"]
        selected_view = row["selected_view"]
        if not isinstance(query_uid, str) or not query_uid:
            raise ValidationError(f"Decision {index} has an invalid query_uid")
        if not isinstance(selected_view, str) or selected_view not in EXPECTED_VIEWS:
            raise ValidationError(f"Decision {index} has an unknown selected_view")
        rows.append(
            {"query_uid": query_uid, "selected_view": selected_view}
        )
    frame = pd.DataFrame(rows)
    if frame["query_uid"].nunique() != 2_001:
        duplicates = frame.loc[
            frame["query_uid"].duplicated(), "query_uid"
        ].head(5)
        raise ValidationError(f"Duplicate query_uid values: {duplicates.tolist()}")
    expected_ids = set(
        splits.loc[
            (splits["seed"] == seed) & (splits["partition"] == "test"),
            "query_uid",
        ].astype(str)
    )
    observed_ids = set(frame["query_uid"])
    missing = sorted(expected_ids - observed_ids)
    extra = sorted(observed_ids - expected_ids)
    if missing or extra:
        raise ValidationError(
            f"Query membership mismatch; missing={missing[:5]}, extra={extra[:5]}"
        )
    if not observed_ids.issubset(set(membership["query_uid"].astype(str))):
        raise ValidationError("Submission contains an ID outside public membership")
    order = {
        query_uid: index for index, query_uid in enumerate(sorted(expected_ids))
    }
    frame["_order"] = frame["query_uid"].map(order)
    frame = (
        frame.sort_values("_order")
        .drop(columns="_order")
        .reset_index(drop=True)
    )
    return submission, frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        submission, frame = validate_submission(
            args.public_root, args.submission
        )
    except ValidationError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        raise SystemExit(2) from exc
    print(
        json.dumps(
            {
                "valid": True,
                "task_id": EXPECTED_TASK_ID,
                "evaluation_seed": submission["evaluation_seed"],
                "policy_id": submission["policy_id"],
                "decisions": len(frame),
                "action_counts": (
                    frame["selected_view"].value_counts().sort_index().to_dict()
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

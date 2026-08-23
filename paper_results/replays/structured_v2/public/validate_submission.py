#!/usr/bin/env python
"""Fail-closed validator for WorthIR Structured-v2 action submissions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


EXPECTED_SURFACE_ID = "worthir-structured-v2-scoring-surface-v1.2"
EXPECTED_TASK_ID = "worthir-2wiki-structured-v2.0"
EXPECTED_SCHEMA_ID = "worthir-structured-v2-submission-v1.1"
EXPECTED_VIEWS = {"summary", "one_hop", "two_hop", "full_context", "ce"}
ROOT_KEYS = {
    "schema_id",
    "task_id",
    "policy_id",
    "decisions",
}
DECISION_KEYS = {"query_uid", "selected_view"}


class ValidationError(RuntimeError):
    """A deterministic, user-facing submission validation failure."""


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


def validate_submission(
    public_root: Path, submission_path: Path
) -> tuple[dict[str, Any], pd.DataFrame]:
    public_root = public_root.resolve()
    verify_manifest(public_root)
    task = load_json(public_root / "contracts" / "task_contract.json")
    route = load_json(public_root / "contracts" / "route_registry.json")
    cost = load_json(public_root / "contracts" / "cost_contract.json")
    membership = pd.read_parquet(
        public_root / "data" / "query_membership.parquet"
    )
    if not {"query_uid", "source_query_id", "outer_fold"}.issubset(
        membership.columns
    ):
        raise ValidationError("Unexpected public membership schema")
    if len(membership) != 2000 or membership["query_uid"].nunique() != 2000:
        raise ValidationError("Public membership must contain 2,000 unique queries")

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
    if cost.get("task_id") != EXPECTED_TASK_ID or route.get("task_id") != EXPECTED_TASK_ID:
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
    if not isinstance(decisions, list) or len(decisions) != 2000:
        raise ValidationError("Submission must contain exactly 2,000 decisions")
    rows: list[dict[str, str]] = []
    for index, row in enumerate(decisions):
        if not isinstance(row, dict) or set(row) != DECISION_KEYS:
            raise ValidationError(
                f"Decision {index} must contain only query_uid and selected_view"
            )
        uid = row["query_uid"]
        view = row["selected_view"]
        if not isinstance(uid, str) or not uid:
            raise ValidationError(f"Decision {index} has an invalid query_uid")
        if not isinstance(view, str) or view not in EXPECTED_VIEWS:
            raise ValidationError(f"Decision {index} has an unknown selected_view")
        rows.append({"query_uid": uid, "selected_view": view})
    frame = pd.DataFrame(rows)
    if frame["query_uid"].nunique() != 2000:
        duplicates = frame.loc[frame["query_uid"].duplicated(), "query_uid"].head(5)
        raise ValidationError(f"Duplicate query_uid values: {duplicates.tolist()}")
    expected_ids = set(membership["query_uid"].astype(str))
    observed_ids = set(frame["query_uid"])
    missing = sorted(expected_ids - observed_ids)
    extra = sorted(observed_ids - expected_ids)
    if missing or extra:
        raise ValidationError(
            f"Query membership mismatch; missing={missing[:5]}, extra={extra[:5]}"
        )
    order = {uid: i for i, uid in enumerate(membership["query_uid"].astype(str))}
    frame["_order"] = frame["query_uid"].map(order)
    frame = frame.sort_values("_order").drop(columns="_order").reset_index(drop=True)
    return submission, frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        submission, frame = validate_submission(args.public_root, args.submission)
    except ValidationError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        raise SystemExit(2) from exc
    print(
        json.dumps(
            {
                "valid": True,
                "task_id": EXPECTED_TASK_ID,
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

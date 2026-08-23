#!/usr/bin/env python3
"""Verify the compact canonical TREC-DL release structure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    public = root / "public"
    private = root / "organizer_private"

    required = [
        public / "contracts" / "task_contract.json",
        public / "contracts" / "route_registry.json",
        public / "data" / "test" / "2019" / "legal_state.parquet",
        public / "data" / "test" / "2019" / "query_membership.parquet",
        public / "data" / "test" / "2020" / "legal_state.parquet",
        public / "data" / "test" / "2020" / "query_membership.parquet",
        private / "data" / "test" / "2019" / "route_outcomes.parquet",
        private / "data" / "test" / "2020" / "route_outcomes.parquet",
    ]
    missing = [
        str(path.relative_to(root)) for path in required if not path.is_file()
    ]
    empty = [
        str(path.relative_to(root))
        for path in required
        if path.is_file() and path.stat().st_size == 0
    ]
    excluded_material_absent = (
        not (public / "data" / "development").exists()
        and not (private / "audit").exists()
    )
    status = (
        "PASS"
        if not missing and not empty and excluded_material_absent
        else "FAIL"
    )
    payload = {
        "status": status,
        "required_files": len(required),
        "missing": missing,
        "empty": empty,
        "excluded_upstream_material_absent": excluded_material_absent,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(0 if status == "PASS" else 2)


if __name__ == "__main__":
    main()

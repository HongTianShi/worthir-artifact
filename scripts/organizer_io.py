"""Shared output handling for evaluator-only WorthIR analyses."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


def output_path(task: Path, requested: Path | None, default_name: str) -> Path:
    task = task.resolve()
    destination = (
        requested.resolve()
        if requested is not None
        else task / "organizer_private" / default_name
    )
    participant = (task / "participant").resolve()
    if destination == participant or participant in destination.parents:
        raise ValueError("evaluator-only output cannot be written under participant/")
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def parse_grid(value: str, name: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise ValueError(f"{name} must be a comma-separated numeric grid") from exc
    if not values or any(not math.isfinite(item) or item < 0 for item in values):
        raise ValueError(f"{name} must contain finite nonnegative values")
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must not repeat values")
    return values


def declared_grid(task: Path, field: str) -> list[float]:
    contract = json.loads(
        (task / "contracts" / "task_contract.json").read_text(encoding="utf-8")
    )
    values = contract.get("cost_profile", {}).get(field)
    if not isinstance(values, list) or not values:
        raise ValueError(
            f"task contract does not declare {field}; provide an explicit grid"
        )
    return [float(value) for value in values]


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("analysis produced no rows")
    if path.suffix.lower() == ".parquet":
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise ValueError(
                "Parquet output requires pyarrow; use .csv or install pyarrow"
            ) from exc
        pq.write_table(pa.Table.from_pylist(rows), path)
        return
    if path.suffix.lower() != ".csv":
        raise ValueError("tabular organizer output must end in .csv or .parquet")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(
            {
                key: f"{value:.12g}" if isinstance(value, float) else value
                for key, value in row.items()
            }
            for row in rows
        )


def write_metadata(path: Path, metadata: dict[str, Any]) -> Path:
    metadata_path = path.with_suffix(path.suffix + ".metadata.json")
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return metadata_path


def same_grid(left: list[float], right: list[float]) -> bool:
    return len(left) == len(right) and all(
        math.isclose(a, b, rel_tol=0.0, abs_tol=1e-12)
        for a, b in zip(left, right)
    )

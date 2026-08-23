#!/usr/bin/env python3
"""Rebuild Figures 1--7 and Tables 2--4 from frozen released inputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path) -> dict[str, Any]:
    start = time.perf_counter()
    process = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return {
        "command": [Path(token).name if index == 1 else token
                    for index, token in enumerate(command)],
        "returncode": process.returncode,
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "stdout": process.stdout,
        "stderr": process.stderr,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def markdown_table(frame: pd.DataFrame) -> str:
    columns = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines) + "\n"


def wilson_interval(successes: int, total: int) -> list[float]:
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    half_width = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return [float(centre - half_width), float(centre + half_width)]


def bootstrap_mean_ci(
    values: np.ndarray,
    *,
    seed: int,
    resamples: int = 10_000,
) -> list[float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    indices = rng.integers(
        0,
        values.size,
        size=(resamples, values.size),
    )
    means = values[indices].mean(axis=1)
    return [
        float(value)
        for value in np.quantile(means, [0.025, 0.975])
    ]


def reproduce_table2(output: Path, steps: list[dict[str, Any]]) -> pd.DataFrame:
    replay = ROOT / "replays" / "canonical_trec"
    atlas_path = output / "table2_health_atlas.json"
    route_order = [
        "stop_bm25",
        "dense_fusion",
        "late_interaction",
        "cross_encoder",
    ]
    tolerance = 1e-12
    atlas: dict[str, Any] = {
        "atlas_id": "worthir-canonical-tie-aware-paper-replay-v1.0",
        "status": "frozen_ledger_recomputation",
        "quality_oracle_rule": (
            "raw-NDCG argmax set; ties use lower cumulative C_op and "
            "then registry order"
        ),
        "utility_oracle_rule": (
            "frozen evaluator oracle, cross-checked against the maximum "
            "stored primary utility"
        ),
        "tracks": {},
    }
    rows = []
    for year in ("2019", "2020"):
        ledger_path = (
            replay
            / "organizer_private"
            / "data"
            / "test"
            / year
            / "route_outcomes.parquet"
        )
        ledger = pd.read_parquet(ledger_path)
        required = {
            "query_uid",
            "route_id",
            "raw_ndcg_at_10",
            "C_op",
            "utility_C_op_lambda_0_08",
            "exact_within_menu_regret",
            "oracle_route_evaluator_only",
            "oracle_utility_evaluator_only",
        }
        if not required.issubset(ledger.columns):
            missing = sorted(required - set(ledger.columns))
            raise RuntimeError(f"Table 2 {year} ledger missing {missing}")
        if ledger.duplicated(["query_uid", "route_id"]).any():
            raise RuntimeError(f"Table 2 {year} has duplicate query-route rows")

        disagreements: list[bool] = []
        quality_oracle_regrets: list[float] = []
        fixed_headrooms: list[float] = []
        quality_oracle_routes: list[str] = []
        utility_oracle_routes: list[str] = []
        for query_uid, group in ledger.groupby("query_uid", sort=True):
            routes = set(group["route_id"])
            if routes != set(route_order):
                raise RuntimeError(
                    f"Table 2 {year} incomplete menu for {query_uid}"
                )
            indexed = group.set_index("route_id")
            raw_quality = indexed["raw_ndcg_at_10"].astype(float)
            costs = indexed["C_op"].astype(float)
            utility = indexed["utility_C_op_lambda_0_08"].astype(float)
            if not np.allclose(
                utility.to_numpy(),
                raw_quality.to_numpy() - 0.08 * costs.to_numpy(),
                rtol=0.0,
                atol=tolerance,
            ):
                raise RuntimeError(
                    f"Table 2 {year} utility arithmetic mismatch for {query_uid}"
                )

            max_quality = float(raw_quality.max())
            quality_candidates = [
                route
                for route in route_order
                if abs(float(raw_quality[route]) - max_quality) <= tolerance
            ]
            quality_route = min(
                quality_candidates,
                key=lambda route: (
                    float(costs[route]),
                    route_order.index(route),
                ),
            )

            max_utility = float(utility.max())
            utility_candidates = [
                route
                for route in route_order
                if abs(float(utility[route]) - max_utility) <= tolerance
            ]
            utility_route = min(
                utility_candidates,
                key=lambda route: (
                    float(costs[route]),
                    route_order.index(route),
                ),
            )
            stored_oracles = group["oracle_route_evaluator_only"].unique()
            stored_utilities = group["oracle_utility_evaluator_only"].unique()
            if (
                len(stored_oracles) != 1
                or stored_oracles[0] != utility_route
                or len(stored_utilities) != 1
                or not math.isclose(
                    float(stored_utilities[0]),
                    max_utility,
                    rel_tol=0.0,
                    abs_tol=tolerance,
                )
            ):
                raise RuntimeError(
                    f"Table 2 {year} frozen oracle mismatch for {query_uid}"
                )
            ce_regret = float(
                indexed.loc["cross_encoder", "exact_within_menu_regret"]
            )
            recomputed_ce_regret = (
                max_utility - float(utility["cross_encoder"])
            )
            if not math.isclose(
                ce_regret,
                recomputed_ce_regret,
                rel_tol=0.0,
                abs_tol=tolerance,
            ):
                raise RuntimeError(
                    f"Table 2 {year} frozen regret mismatch for {query_uid}"
                )

            quality_oracle_routes.append(quality_route)
            utility_oracle_routes.append(utility_route)
            disagreements.append(quality_route != utility_route)
            quality_oracle_regrets.append(
                max_utility - float(utility[quality_route])
            )
            fixed_headrooms.append(recomputed_ce_regret)

        queries = len(disagreements)
        count = int(sum(disagreements))
        regret_values = np.asarray(quality_oracle_regrets, dtype=float)
        headroom_values = np.asarray(fixed_headrooms, dtype=float)
        regret_ci = bootstrap_mean_ci(
            regret_values,
            seed=20_263_700 + int(year),
        )
        headroom_ci = bootstrap_mean_ci(
            headroom_values,
            seed=20_264_700 + int(year),
        )
        track = {
            "queries": queries,
            "raw_quality_vs_primary_utility_oracle_disagreement_count": count,
            "raw_quality_vs_primary_utility_oracle_disagreement_rate":
                count / queries,
            "raw_quality_vs_primary_utility_oracle_disagreement_wilson_ci95":
                wilson_interval(count, queries),
            "primary_utility_regret_of_raw_quality_oracle": {
                "mean": float(regret_values.mean()),
                "mean_ci95": regret_ci,
            },
            "fixed_to_oracle_headroom": float(headroom_values.mean()),
            "fixed_to_oracle_headroom_ci95": headroom_ci,
            "queries_with_positive_fixed_to_oracle_headroom_count": int(
                np.sum(headroom_values > tolerance)
            ),
            "queries_with_positive_fixed_to_oracle_headroom": float(
                np.mean(headroom_values > tolerance)
            ),
            "quality_oracle_route_share": {
                route: quality_oracle_routes.count(route) / queries
                for route in route_order
            },
            "utility_oracle_route_share": {
                route: utility_oracle_routes.count(route) / queries
                for route in route_order
            },
        }
        atlas["tracks"][year] = track
        regret = track["primary_utility_regret_of_raw_quality_oracle"]
        rows.append(
            {
                "track": f"TREC DL {year}",
                "development_fixed_quality": "cross_encoder",
                "development_fixed_utility": "cross_encoder",
                "oracle_disagreement_count": count,
                "queries": queries,
                "oracle_disagreement_percent": 100.0 * count / queries,
                "wilson_low_percent": 100.0
                * track[
                    "raw_quality_vs_primary_utility_oracle_disagreement_wilson_ci95"
                ][0],
                "wilson_high_percent": 100.0
                * track[
                    "raw_quality_vs_primary_utility_oracle_disagreement_wilson_ci95"
                ][1],
                "quality_oracle_utility_regret": regret["mean"],
                "regret_ci_low": regret["mean_ci95"][0],
                "regret_ci_high": regret["mean_ci95"][1],
                "fixed_to_oracle_headroom": track["fixed_to_oracle_headroom"],
                "headroom_ci_low": track["fixed_to_oracle_headroom_ci95"][0],
                "headroom_ci_high": track["fixed_to_oracle_headroom_ci95"][1],
                "positive_headroom_count": int(
                    track[
                        "queries_with_positive_fixed_to_oracle_headroom_count"
                    ]
                ),
            }
        )
    write_json(atlas_path, atlas)
    steps.append(
        {
            "id": "table2_tie_aware_ledger_recompute",
            "returncode": 0,
            "elapsed_seconds": None,
            "stdout": (
                "recomputed from frozen per-query route ledgers and "
                "cross-checked evaluator oracle/regret fields"
            ),
            "stderr": "",
        }
    )
    frame = pd.DataFrame(rows)
    expected = {
        "2019": {
            "count": 13,
            "queries": 43,
            "regret": 0.014147,
            "headroom": 0.025917,
            "positive": 14,
        },
        "2020": {
            "count": 14,
            "queries": 54,
            "regret": 0.009691,
            "headroom": 0.036325,
            "positive": 24,
        },
    }
    for row, year in zip(rows, ("2019", "2020")):
        target = expected[year]
        if row["oracle_disagreement_count"] != target["count"]:
            raise RuntimeError(f"Table 2 {year} disagreement mismatch")
        if row["queries"] != target["queries"]:
            raise RuntimeError(f"Table 2 {year} query count mismatch")
        if row["positive_headroom_count"] != target["positive"]:
            raise RuntimeError(f"Table 2 {year} positive-headroom mismatch")
        if not math.isclose(
            row["quality_oracle_utility_regret"],
            target["regret"],
            abs_tol=5e-7,
        ):
            raise RuntimeError(f"Table 2 {year} regret mismatch")
        if not math.isclose(
            row["fixed_to_oracle_headroom"],
            target["headroom"],
            abs_tol=5e-7,
        ):
            raise RuntimeError(f"Table 2 {year} headroom mismatch")
    frame.to_csv(output / "table2_canonical_heldout.csv", index=False)
    (output / "table2_canonical_heldout.md").write_text(
        markdown_table(frame.round(6)),
        encoding="utf-8",
    )
    return frame


def reproduce_table3(output: Path) -> pd.DataFrame:
    source = (
        ROOT
        / "paper_reproduction"
        / "inputs"
        / "table3_recoverability.csv"
    )
    frame = pd.read_csv(source)
    failures: list[str] = []
    for row in frame.itertuples(index=False):
        delta_dev = row.valid_adaptive - row.f_dev
        delta_tih = row.valid_adaptive - row.f_tih
        headroom_dev = row.o_tih - row.f_dev
        headroom_tih = row.o_tih - row.f_tih
        kappa_dev = 100.0 * delta_dev / headroom_dev
        kappa_tih = 100.0 * delta_tih / headroom_tih
        if not math.isclose(delta_dev, row.delta_dev, abs_tol=1.5e-6):
            failures.append(f"{row.task}: delta_dev")
        if not math.isclose(delta_tih, row.delta_tih, abs_tol=1.5e-6):
            failures.append(f"{row.task}: delta_tih")
        if not math.isclose(kappa_dev, row.kappa_dev_percent, abs_tol=0.015):
            failures.append(f"{row.task}: kappa_dev")
        if not math.isclose(kappa_tih, row.kappa_tih_percent, abs_tol=0.015):
            failures.append(f"{row.task}: kappa_tih")
    if failures:
        raise RuntimeError(f"Table 3 arithmetic mismatch: {failures}")
    frame.to_csv(output / "table3_recoverability.csv", index=False)
    (output / "table3_recoverability.md").write_text(
        markdown_table(frame),
        encoding="utf-8",
    )
    return frame


def reproduce_table4(output: Path) -> pd.DataFrame:
    source = (
        ROOT
        / "paper_reproduction"
        / "inputs"
        / "table4_query_level.parquet"
    )
    frame = pd.read_parquet(source)
    expected_columns = {
        "population",
        "query_id",
        "condition",
        "support_recall",
        "any_support",
        "all_support",
    }
    if not expected_columns.issubset(frame.columns):
        raise RuntimeError("Table 4 query-level source schema mismatch")
    selected = frame[
        frame["condition"].isin(["base_top10", "base5_one5"])
    ].copy()
    aggregate = (
        selected.groupby(["population", "condition"], as_index=False)
        .agg(
            queries=("query_id", "nunique"),
            mean_support_recall=("support_recall", "mean"),
            any_support_coverage=("any_support", "mean"),
            all_support_coverage=("all_support", "mean"),
        )
        .sort_values(["population", "condition"])
        .reset_index(drop=True)
    )
    expected = pd.read_csv(
        ROOT / "paper_reproduction" / "inputs" / "table4_expected.csv"
    )
    expected = expected[
        expected["condition"].isin(["base_top10", "base5_one5"])
    ][
        [
            "population",
            "condition",
            "queries",
            "mean_support_recall",
            "any_support_coverage",
            "all_support_coverage",
        ]
    ].sort_values(["population", "condition"]).reset_index(drop=True)
    if list(aggregate[["population", "condition"]].itertuples(index=False, name=None)) != list(
        expected[["population", "condition"]].itertuples(index=False, name=None)
    ):
        raise RuntimeError("Table 4 population/condition mismatch")
    numeric = [
        "queries",
        "mean_support_recall",
        "any_support_coverage",
        "all_support_coverage",
    ]
    if not all(
        math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-12)
        for column in numeric
        for left, right in zip(aggregate[column], expected[column])
    ):
        raise RuntimeError("Table 4 aggregation mismatch")
    labels = {
        "structured2k": "2Wiki 2k",
        "hyperlink10k": "Hyperlink 10k",
        "base_top10": "lexical top-10",
        "base5_one5": "lexical5 + 1-hop5",
    }
    display = aggregate.copy()
    display["population"] = display["population"].map(labels)
    display["condition"] = display["condition"].map(labels)
    for column in (
        "mean_support_recall",
        "any_support_coverage",
        "all_support_coverage",
    ):
        display[column] = 100.0 * display[column]
    display.to_csv(output / "table4_matched_top10.csv", index=False)
    (output / "table4_matched_top10.md").write_text(
        markdown_table(display.round(2)),
        encoding="utf-8",
    )
    return display


def run_native_replays(output: Path, steps: list[dict[str, Any]]) -> None:
    structured = ROOT / "replays" / "structured_v2"
    commands = [
        (
            "structured_v2_frozen_actions",
            [
                sys.executable,
                str(structured / "organizer_private" / "score_submission.py"),
                "--public-root",
                str(structured / "public"),
                "--private-root",
                str(structured / "organizer_private"),
                "--submission",
                str(
                    structured
                    / "organizer_private"
                    / "golden_submissions"
                    / "frozen_a_oof.json"
                ),
                "--output",
                str(output / "native_structured_v2_score.json"),
            ],
        ),
        (
            "fever_frozen_actions",
            [
                sys.executable,
                str(ROOT / "replays" / "fever" / "scripts" / "score_actions.py"),
                "--bundle-root",
                str(ROOT / "replays" / "fever"),
                "--actions",
                str(
                    ROOT
                    / "replays"
                    / "fever"
                    / "frozen_results"
                    / "registered_actions_lambda08.csv"
                ),
                "--lambda-value",
                "0.08",
                "--output",
                str(output / "native_fever_score.json"),
            ],
        ),
        (
            "musique_frozen_actions",
            [
                sys.executable,
                str(
                    ROOT
                    / "replays"
                    / "musique"
                    / "scripts"
                    / "score_action_file.py"
                ),
                "--root",
                str(ROOT / "replays" / "musique"),
                "--actions",
                str(
                    ROOT
                    / "replays"
                    / "musique"
                    / "examples"
                    / "official_validation_actions.parquet"
                ),
                "--cost-profile",
                "relative_v1",
                "--lambda-value",
                "0.08",
                "--output",
                str(output / "native_musique_score.json"),
            ],
        ),
    ]
    for step_id, command in commands:
        result = run(command, ROOT)
        steps.append({"id": step_id, **result})
        if result["returncode"] != 0:
            raise RuntimeError(f"{step_id} failed: {result['stderr']}")

    structured_score = json.loads(
        (output / "native_structured_v2_score.json").read_text(encoding="utf-8")
    )
    fever_score = json.loads(
        (output / "native_fever_score.json").read_text(encoding="utf-8")
    )
    musique_score = json.loads(
        (output / "native_musique_score.json").read_text(encoding="utf-8")
    )
    checks = [
        math.isclose(
            structured_score["aggregate"]["utility"]["estimate"],
            0.925076,
            abs_tol=5e-7,
        ),
        math.isclose(fever_score["mean_utility"], 0.800717, abs_tol=5e-7),
        math.isclose(musique_score["mean_utility"], 0.519406, abs_tol=5e-7),
    ]
    if not all(checks):
        raise RuntimeError("native scorer cross-check does not match Table 3")


def reproduce_figures(output: Path, steps: list[dict[str, Any]]) -> None:
    source = ROOT / "paper_reproduction" / "figures"
    work = output / "figures"
    work.mkdir(parents=True, exist_ok=True)
    for name in (
        "make_worthir_contract.py",
        "hero_example_2019.json",
        "make_cost_quality_inversion.py",
        "cost_quality_inversion_data.csv",
        "make_recoverability_bridge.py",
        "recoverability_bridge_data.csv",
    ):
        shutil.copy2(source / name, work / name)
    commands = [
        (
            "figure1",
            [
                sys.executable,
                str(work / "make_worthir_contract.py"),
                "--input",
                str(work / "hero_example_2019.json"),
                "--output-stem",
                str(work / "figure1"),
            ],
        ),
        (
            "figure2",
            [sys.executable, str(work / "make_cost_quality_inversion.py")],
        ),
        (
            "figure3",
            [sys.executable, str(work / "make_recoverability_bridge.py")],
        ),
        (
            "figures4-7",
            [
                sys.executable,
                str(source / "make_figures_4_7.py"),
                "--data-root",
                str(ROOT),
                "--output-dir",
                str(work),
            ],
        ),
    ]
    for step_id, command in commands:
        result = run(command, work)
        steps.append({"id": step_id, **result})
        if result["returncode"] != 0:
            raise RuntimeError(f"{step_id} failed: {result['stderr']}")
    required = (
        "figure1.pdf",
        "cost_quality_final.pdf",
        "recoverability_bridge.pdf",
        "figure4.pdf",
        "figure5.pdf",
        "figure6.pdf",
        "figure7.pdf",
    )
    missing = [name for name in required if not (work / name).is_file()]
    if missing:
        raise RuntimeError(f"missing generated figures: {missing}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skip-figures", action="store_true")
    parser.add_argument("--skip-native-scorers", action="store_true")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"refusing nonempty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    steps: list[dict[str, Any]] = []
    started = time.perf_counter()
    try:
        table2 = reproduce_table2(output, steps)
        table3 = reproduce_table3(output)
        table4 = reproduce_table4(output)
        if not args.skip_native_scorers:
            run_native_replays(output, steps)
        if not args.skip_figures:
            reproduce_figures(output, steps)
        status = "PASS"
        error = None
    except Exception as exc:
        status = "FAIL"
        error = str(exc)
        table2 = table3 = table4 = pd.DataFrame()
    report = {
        "status": status,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "tables": {
            "table2_rows": len(table2),
            "table3_rows": len(table3),
            "table4_rows": len(table4),
        },
        "steps": steps,
        "error": error,
        "scope": (
            "frozen ledger/readout replay only; no route inference, fitting, "
            "or model selection"
        ),
    }
    write_json(output / "reproduction_report.json", report)
    print(
        json.dumps(
            {
                "status": status,
                "elapsed_seconds": report["elapsed_seconds"],
                "output_dir": str(output),
                "error": error,
            },
            indent=2,
        )
    )
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()

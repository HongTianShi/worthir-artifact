#!/usr/bin/env python3
"""Rebuild the compact RQ2--RQ5 readouts from released artifact records."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import pandas as pd


LAMBDA = 0.08
DISPLAY_TASK = {
    "trec_dl": "TREC-DL pooled",
    "fever": "FEVER",
    "structured_v2": "2Wiki-Structured",
    "musique": "MuSiQue",
}


def load_ledgers(root: Path) -> dict[str, pd.DataFrame]:
    trec_parts = []
    for year in ("2019", "2020"):
        path = (
            root
            / "replays"
            / "canonical_trec"
            / "organizer_private"
            / "data"
            / "test"
            / year
            / "route_outcomes.parquet"
        )
        frame = pd.read_parquet(path).rename(
            columns={
                "route_id": "route",
                "raw_ndcg_at_10": "quality",
                "C_op": "cost",
                "utility_C_op_lambda_0_08": "utility",
            }
        )
        trec_parts.append(frame[["query_uid", "route", "quality", "cost", "utility"]])

    fever_outcomes = pd.read_parquet(
        root / "replays" / "fever" / "organizer_private" / "test_outcomes.parquet"
    )
    fever_costs = pd.read_parquet(
        root / "replays" / "fever" / "organizer_private" / "route_costs.parquet"
    )
    fever_costs = fever_costs.loc[
        fever_costs["evaluation_role"].eq("official_dev_test"),
        ["query_uid", "route", "cost_work"],
    ]
    fever = fever_outcomes.merge(
        fever_costs, on=["query_uid", "route"], validate="one_to_one"
    ).rename(columns={"raw_ndcg_10": "quality", "cost_work": "cost"})
    fever["utility"] = fever["quality"] - LAMBDA * fever["cost"]

    structured = pd.read_parquet(
        root
        / "replays"
        / "structured_v2"
        / "organizer_private"
        / "data"
        / "outcomes.parquet"
    ).rename(
        columns={"view": "route", "raw_quality": "quality", "declared_cost": "cost"}
    )
    structured["utility"] = structured["quality"] - LAMBDA * structured["cost"]

    musique = pd.read_parquet(
        root
        / "replays"
        / "musique"
        / "organizer_private"
        / "route_outcomes_private.parquet"
    )
    musique = musique.loc[musique["split"].eq("test")].rename(
        columns={"ndcg_at_4": "quality", "operator_cost": "cost"}
    )

    return {
        "trec_dl": pd.concat(trec_parts, ignore_index=True),
        "fever": fever[["query_uid", "route", "quality", "cost", "utility"]],
        "structured_v2": structured[
            ["query_uid", "route", "quality", "cost", "utility"]
        ],
        "musique": musique[["query_uid", "route", "quality", "cost", "utility"]],
    }


def score_actions(actions: pd.DataFrame, ledger: pd.DataFrame) -> dict[str, float | int]:
    joined = actions[["query_uid", "route"]].merge(
        ledger, on=["query_uid", "route"], how="left", validate="one_to_one"
    )
    if joined[["quality", "cost", "utility"]].isna().any().any():
        raise ValueError("an action does not match the released route ledger")
    return {
        "queries": int(len(joined)),
        "mean_quality": float(joined["quality"].mean()),
        "mean_cost": float(joined["cost"].mean()),
        "mean_utility": float(joined["utility"].mean()),
    }


def reproduce_rq2(root: Path) -> tuple[pd.DataFrame, dict[str, int]]:
    base = root / "analyses" / "rq2_policy_comparison"
    non_neural = pd.read_parquet(base / "actions" / "non_neural_actions.parquet")
    arr = pd.read_parquet(base / "actions" / "arr_actions.parquet")
    expected = pd.read_csv(base / "results" / "policy_comparison.csv")
    ledgers = load_ledgers(root)
    rows: list[dict[str, float | int | str]] = []

    for task, ledger in ledgers.items():
        policies = ["fixed", "qpp", "native_adaptive"]
        policies.extend(f"arr_seed_{index}" for index in range(1, 6))
        for policy in policies:
            source = arr if policy.startswith("arr_") else non_neural
            actions = source.loc[
                source["task"].eq(task) & source["policy"].eq(policy)
            ]
            scores = score_actions(actions, ledger)
            registered = expected.loc[
                expected["task"].eq(task) & expected["policy"].eq(policy)
            ].iloc[0]
            for column in ("mean_quality", "mean_cost", "mean_utility"):
                if abs(scores[column] - float(registered[column])) > 1e-10:
                    raise ValueError(f"RQ2 mismatch for {task}/{policy}/{column}")
            rows.append(
                {
                    "task": DISPLAY_TASK[task],
                    "policy": policy,
                    **scores,
                    "delta_utility_vs_fixed": float(
                        registered["delta_utility_vs_fixed"]
                    ),
                    "ci_low": float(registered["delta_vs_fixed_ci_low"])
                    if pd.notna(registered["delta_vs_fixed_ci_low"])
                    else None,
                    "ci_high": float(registered["delta_vs_fixed_ci_high"])
                    if pd.notna(registered["delta_vs_fixed_ci_high"])
                    else None,
                }
            )

        route_average = ledger.groupby("query_uid")[["quality", "cost", "utility"]].mean()
        registered = expected.loc[
            expected["task"].eq(task)
            & expected["policy"].eq("uniform_random_analytic")
        ].iloc[0]
        for source_column, expected_column in (
            ("quality", "mean_quality"),
            ("cost", "mean_cost"),
            ("utility", "mean_utility"),
        ):
            value = float(route_average[source_column].mean())
            if abs(value - float(registered[expected_column])) > 1e-10:
                raise ValueError(f"RQ2 uniform-random mismatch for {task}")
        rows.append(
            {
                "task": DISPLAY_TASK[task],
                "policy": "uniform_random_analytic",
                "queries": int(route_average.shape[0]),
                "mean_quality": float(route_average["quality"].mean()),
                "mean_cost": float(route_average["cost"].mean()),
                "mean_utility": float(route_average["utility"].mean()),
                "delta_utility_vs_fixed": float(
                    registered["delta_utility_vs_fixed"]
                ),
                "ci_low": None,
                "ci_high": None,
            }
        )

    # The route-independent control is defined by a probability vector per
    # task/policy. Recompute its analytic expected quality, cost, and utility.
    probability_table = pd.read_csv(
        base / "actions" / "expected_cost_control_probabilities.csv"
    )
    control_table = pd.read_csv(base / "results" / "expected_cost_controls.csv")
    control_checks = 0
    for row in probability_table.itertuples(index=False):
        probabilities = json.loads(row.route_probabilities)
        route_means = ledgers[row.task].groupby("route")[["quality", "cost", "utility"]].mean()
        expected_values = {
            column: sum(float(probability) * float(route_means.loc[route, column])
                        for route, probability in probabilities.items())
            for column in ("quality", "cost", "utility")
        }
        registered = control_table.loc[
            control_table["task"].eq(row.task)
            & control_table["policy"].eq(row.policy)
        ].iloc[0]
        for column in ("quality", "cost", "utility"):
            if abs(expected_values[column] - float(registered[f"analytic_mean_{column}"])) > 1e-10:
                raise ValueError(f"RQ2 expected-cost control mismatch for {row.task}/{row.policy}")
        control_checks += 1

    # Re-score the FEVER three- and five-route comparison. ET-5, QPP-3/5,
    # and ARR-5 are already present in the cross-task action files; the two
    # companion files add ET-3 and the five ARR-3 seeds.
    fever_ledger = ledgers["fever"]
    same_menu_expected = pd.read_csv(
        base / "results" / "fever_same_menu_policy_comparison.csv"
    ).set_index("policy")
    companion = pd.read_csv(base / "actions" / "fever_same_menu_actions.csv")
    arr_companion = pd.read_csv(
        base / "actions" / "fever_arr_3_and_5_route_actions.csv"
    )
    qpp_actions = non_neural.loc[
        non_neural["task"].eq("fever") & non_neural["policy"].eq("qpp"),
        ["query_uid", "route"],
    ]
    et5_actions = non_neural.loc[
        non_neural["task"].eq("fever")
        & non_neural["policy"].eq("native_adaptive"),
        ["query_uid", "route"],
    ]
    primary_arr5 = arr.loc[
        arr["task"].eq("fever") & arr["policy"].eq("arr_seed_1"),
        ["query_uid", "route"],
    ]
    same_menu_actions = {
        "extratrees3": companion[["query_uid", "et3"]].rename(columns={"et3": "route"}),
        "qpp3": qpp_actions,
        "arr3": arr_companion[["query_uid", "arr3_seed20260807"]].rename(
            columns={"arr3_seed20260807": "route"}
        ),
        "extratrees5": et5_actions,
        "qpp5": qpp_actions,
        "arr5": primary_arr5,
    }
    same_menu_checks = 0
    same_menu_scores: dict[str, float] = {}
    for policy, actions in same_menu_actions.items():
        score = score_actions(actions, fever_ledger)
        expected_utility = float(same_menu_expected.loc[policy, "mean_utility"])
        if abs(float(score["mean_utility"]) - expected_utility) > 1e-10:
            raise ValueError(f"RQ2 FEVER same-menu mismatch for {policy}")
        same_menu_scores[policy] = float(score["mean_utility"])
        same_menu_checks += 1
    pairwise = pd.read_csv(base / "results" / "fever_pairwise_comparison.csv")
    for menu_size in (3, 5):
        expected_difference = float(
            pairwise.loc[pairwise["menu_size"].eq(menu_size), "mean"].iloc[0]
        )
        observed_difference = (
            same_menu_scores[f"extratrees{menu_size}"]
            - same_menu_scores[f"qpp{menu_size}"]
        )
        if abs(observed_difference - expected_difference) > 1e-10:
            raise ValueError(f"RQ2 FEVER ET-QPP contrast mismatch for menu {menu_size}")

    matching = pd.read_csv(
        base / "results" / "fever_query_route_matching.csv"
    )
    if "route_mix_effect" in matching.columns:
        net = matching["route_mix_effect"] + matching["query_alignment_effect"]
        if not (net - matching["net_effect"]).abs().lt(2e-10).all():
            raise ValueError("RQ2 FEVER route-mix/matching decomposition does not close")

    return pd.DataFrame(rows), {
        "tasks": len(ledgers),
        "policies_scored": len(rows),
        "action_rows": int(len(non_neural) + len(arr)),
        "expected_cost_controls": control_checks,
        "fever_same_menu_policies": same_menu_checks,
        "fever_pairwise_contrasts": 2,
        "fever_matching_decompositions": int(len(matching)),
    }


def validate_rq3(root: Path) -> dict[str, int]:
    base = root / "analyses" / "rq3_utility_sources" / "data"
    strata = pd.read_csv(base / "query_strata.csv")
    switching = pd.read_csv(base / "top_decile_switching.csv")
    for task, frame in strata.groupby("task"):
        if frame["stratum_queries"].sum() != frame["queries"].iloc[0]:
            raise ValueError(f"RQ3 stratum counts do not close for {task}")
        contribution = frame["utility_gain_contribution_per_query"].sum()
        headline = frame["headline_utility_gain"].iloc[0]
        if abs(contribution - headline) > 2e-10:
            raise ValueError(f"RQ3 utility contributions do not close for {task}")
    if not ((switching["roc_auc"] >= 0) & (switching["roc_auc"] <= 1)).all():
        raise ValueError("RQ3 AUC is outside [0,1]")
    return {"task_strata": int(len(strata)), "selective_policies": int(len(switching))}


def validate_rq4(root: Path) -> dict[str, int]:
    base = root / "analyses" / "rq4_robustness" / "data"
    preference = pd.read_csv(base / "cost_preference_summary.csv")
    recurrence = pd.read_csv(base / "structured_candidate_recurrence.csv")
    folds = pd.read_csv(base / "model_and_fold_summary.csv")
    dependence = pd.read_csv(base / "fever_candidate_dependence.csv")
    schedules = preference.loc[
        preference["analysis_mode"].eq("fixed_policy_monotone_schedules")
    ].iloc[0]
    if int(schedules["positive_comparisons"]) != 816:
        raise ValueError("RQ4 monotone-schedule count does not match")
    if not (recurrence["bootstrap_ci_low"] > 0).all():
        raise ValueError("RQ4 recurrence stress includes a nonpositive interval")
    reruns = folds.loc[
        folds["test"].eq("full_fold_reassignment_refit_reselection")
    ].iloc[0]
    if int(reruns["positive_intervals_or_runs"]) != 20:
        raise ValueError("RQ4 fold-rerun count does not match")
    if int(dependence["candidate_sharing_components"].iloc[0]) != 1:
        raise ValueError("RQ4 FEVER candidate graph summary does not match")
    return {
        "preference_rows": int(len(preference)),
        "recurrence_thresholds": int(len(recurrence)),
        "model_and_fold_rows": int(len(folds)),
    }


def validate_rq5(root: Path) -> dict[str, int]:
    base = root / "analyses" / "rq5_route_value" / "data"
    prediction = pd.read_csv(base / "rq5_route_value_prediction_summary.csv")
    controls = pd.read_csv(base / "rq5_operation_control_summary.csv")
    fever_depth = pd.read_csv(base / "rq5_fever_gold_rank_band_routes.csv")
    difficulty = pd.read_csv(base / "difficulty_opportunity_summary.csv")
    if prediction["task"].nunique() != 4:
        raise ValueError("RQ5 predictive summary does not cover four tasks")
    required_controls = {
        "V2_vs_shuffled_V2",
        "V3_vs_wrong_decomposition_V3",
        "real_1hop_vs_degree_random_1hop",
        "real_1hop_vs_shuffled_1hop",
        "real_2hop_vs_random_2hop",
    }
    if not required_controls.issubset(set(controls["comparison"])):
        raise ValueError("RQ5 operation controls are incomplete")
    required_depth = {
        ("ce20_minus_bm25", "rank11_20"),
        ("ce100_minus_ce20", "rank21_100"),
        ("hybrid_minus_ce100", "rank101_200"),
        ("ce20_minus_bm25", "absent_top200"),
    }
    observed_depth = set(zip(fever_depth["contrast"], fever_depth["gold_rank_band"]))
    if not required_depth.issubset(observed_depth):
        raise ValueError("RQ5 FEVER depth contrasts are incomplete")
    if difficulty["task"].nunique() != 4:
        raise ValueError("RQ5 difficulty/opportunity summary is incomplete")
    return {
        "prediction_rows": int(len(prediction)),
        "operation_controls": int(len(controls)),
        "fever_depth_rows": int(len(fever_depth)),
    }


def write_summary(output: Path, rq2: pd.DataFrame) -> None:
    focus = rq2.loc[
        rq2["policy"].isin(
            ["fixed", "qpp", "native_adaptive", "uniform_random_analytic"]
        ),
        ["task", "policy", "mean_utility", "delta_utility_vs_fixed"],
    ]
    lines = [
        "# Reproduced RQ readouts",
        "",
        "This run scores the released action vectors against the released route ledgers and checks the compact post-hoc analysis tables. It does not rerun retrieval models.",
        "",
        "## RQ2: shared-evaluator policy comparison",
        "",
        "| Task | Policy | Mean utility | Delta vs fixed |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in focus.itertuples(index=False):
        lines.append(
            f"| {row.task} | {row.policy} | {row.mean_utility:.6f} | {row.delta_utility_vs_fixed:+.6f} |"
        )
    lines.extend(
        [
            "",
            "## RQ3--RQ5",
            "",
            "The run also checks that RQ3 utility contributions sum to each task's headline gain, that the released RQ4 perturbation counts and intervals match the reported summaries, and that the RQ5 prediction, operation-control, and relevant-document-depth readouts are present.",
            "",
            "See the copied CSV files in this directory for the compact numerical readouts.",
        ]
    )
    (output / "RQ_READOUTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"refusing nonempty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    rq2, rq2_checks = reproduce_rq2(root)
    rq3_checks = validate_rq3(root)
    rq4_checks = validate_rq4(root)
    rq5_checks = validate_rq5(root)
    rq2.to_csv(output / "rq2_policy_comparison.csv", index=False)

    copies = {
        root
        / "analyses"
        / "rq2_policy_comparison"
        / "results"
        / "holm_tests.csv": "rq2_holm_tests.csv",
        root
        / "analyses"
        / "rq2_policy_comparison"
        / "results"
        / "fever_same_menu_policy_comparison.csv": "rq2_fever_same_menu.csv",
        root
        / "analyses"
        / "rq3_utility_sources"
        / "data"
        / "query_strata.csv": "rq3_query_strata.csv",
        root
        / "analyses"
        / "rq3_utility_sources"
        / "data"
        / "top_decile_switching.csv": "rq3_top_decile_switching.csv",
        root
        / "analyses"
        / "rq4_robustness"
        / "data"
        / "cost_preference_summary.csv": "rq4_cost_preference.csv",
        root
        / "analyses"
        / "rq4_robustness"
        / "data"
        / "structured_candidate_recurrence.csv": "rq4_candidate_recurrence.csv",
        root
        / "analyses"
        / "rq5_route_value"
        / "data"
        / "rq5_route_value_prediction_summary.csv": "rq5_prediction_summary.csv",
        root
        / "analyses"
        / "rq5_route_value"
        / "data"
        / "rq5_operation_control_summary.csv": "rq5_operation_controls.csv",
    }
    for source, name in copies.items():
        shutil.copyfile(source, output / name)

    report = {
        "status": "PASS",
        "scope": (
            "released action/ledger scoring for RQ2 and compact numerical "
            "closure checks for the post-hoc RQ3--RQ5 analyses"
        ),
        "does_not_run": "retrieval, model training, neural inference, or bootstrap resampling",
        "checks": {"rq2": rq2_checks, "rq3": rq3_checks, "rq4": rq4_checks, "rq5": rq5_checks},
    }
    (output / "reproduction_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_summary(output, rq2)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

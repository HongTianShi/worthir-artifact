#!/usr/bin/env python3
"""Exercise fail-closed and metamorphic properties of the WorthIR scorer."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from worthir_eval import ScoreError, load_and_score  # noqa: E402


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["query_uid", "route_id", "effectiveness", "cost"],
        )
        writer.writeheader()
        writer.writerows(rows)


def read_ledger(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def bind(
    temp: Path,
    contract: dict[str, Any],
    registry: dict[str, Any],
    actions: dict[str, Any],
) -> tuple[Path, Path, Path]:
    registry_path = temp / "route_registry.json"
    contract_path = temp / "contract.json"
    action_path = temp / "actions.json"
    write_json(registry_path, registry)
    contract = copy.deepcopy(contract)
    contract["route_registry"] = registry_path.name
    write_json(contract_path, contract)
    actions = copy.deepcopy(actions)
    actions["contract_id"] = contract["contract_id"]
    write_json(action_path, actions)
    return contract_path, action_path, registry_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reproduced" / "integrity.json",
    )
    args = parser.parse_args()
    base_contract = json.loads(
        (ROOT / "contracts" / "quickstart_contract.json").read_text(encoding="utf-8")
    )
    base_registry = json.loads(
        (ROOT / "contracts" / "route_registry.json").read_text(encoding="utf-8")
    )
    base_actions = json.loads(
        (ROOT / "quickstart" / "participant" / "example_actions.json").read_text(
            encoding="utf-8"
        )
    )
    base_ledger_path = ROOT / "quickstart" / "evaluator" / "hidden_ledger.csv"
    base_rows = read_ledger(base_ledger_path)
    probes: list[dict[str, Any]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        probes.append(
            {"probe": name, "status": "pass" if passed else "fail", "detail": detail}
        )

    def expect_rejection(name: str, fn: Callable[[], Any], fragment: str) -> None:
        try:
            fn()
        except ScoreError as exc:
            record(name, fragment in str(exc), str(exc))
        else:
            record(name, False, "unexpectedly accepted")

    baseline = load_and_score(
        ROOT / "contracts" / "quickstart_contract.json",
        base_ledger_path,
        ROOT / "quickstart" / "participant" / "example_actions.json",
    )
    record(
        "I01_VALID_SCORE_AND_EXACT_ARITHMETIC",
        math.isclose(baseline["mean_utility"], 0.705333333333, abs_tol=1e-12)
        and math.isclose(
            baseline["mean_exact_within_route_set_regret"],
            0.004666666667,
            abs_tol=1e-12,
        ),
        (
            f"utility={baseline['mean_utility']:.15f}, "
            f"regret={baseline['mean_exact_within_route_set_regret']:.15f}"
        ),
    )
    privacy_text = json.dumps(baseline, sort_keys=True)
    record(
        "I02_AGGREGATE_RESPONSE_HAS_NO_QUERY_ROWS",
        all(query_uid not in privacy_text for query_uid in ("q01", "q02", "q03")),
        "aggregate score contains no query identifiers",
    )

    invariant_keys = (
        "mean_effectiveness",
        "mean_cost",
        "mean_utility",
        "mean_exact_within_route_set_regret",
        "oracle_match_share",
        "action_counts",
    )

    def same_aggregates(left: dict[str, Any], right: dict[str, Any]) -> bool:
        for key in invariant_keys:
            if key == "action_counts":
                if left[key] != right[key]:
                    return False
            elif not math.isclose(
                float(left[key]), float(right[key]), rel_tol=0.0, abs_tol=1e-12
            ):
                return False
        return True

    with tempfile.TemporaryDirectory(prefix="worthir-integrity-") as raw_temp:
        temp = Path(raw_temp)

        mutated = copy.deepcopy(base_actions)
        mutated["decisions"][0]["selected_route_id"] = "__unknown__"
        _, action_path, _ = bind(temp, base_contract, base_registry, mutated)
        expect_rejection(
            "I03_UNKNOWN_ROUTE_REJECTED",
            lambda: load_and_score(
                temp / "contract.json", base_ledger_path, action_path
            ),
            "选择了未注册路线",
        )

        mutated = copy.deepcopy(base_actions)
        mutated["decisions"].pop()
        _, action_path, _ = bind(temp, base_contract, base_registry, mutated)
        expect_rejection(
            "I04_MISSING_QUERY_REJECTED",
            lambda: load_and_score(
                temp / "contract.json", base_ledger_path, action_path
            ),
            "动作数不匹配",
        )

        mutated = copy.deepcopy(base_actions)
        mutated["decisions"][-1] = copy.deepcopy(mutated["decisions"][0])
        _, action_path, _ = bind(temp, base_contract, base_registry, mutated)
        expect_rejection(
            "I05_DUPLICATE_QUERY_REJECTED",
            lambda: load_and_score(
                temp / "contract.json", base_ledger_path, action_path
            ),
            "存在重复 query_uid",
        )

        mutated = copy.deepcopy(base_actions)
        mutated["decisions"][0]["effectiveness"] = 1.0
        _, action_path, _ = bind(temp, base_contract, base_registry, mutated)
        expect_rejection(
            "I06_HIDDEN_DECISION_FIELD_REJECTED",
            lambda: load_and_score(
                temp / "contract.json", base_ledger_path, action_path
            ),
            "字段不匹配",
        )

        mutated = copy.deepcopy(base_actions)
        _, action_path, _ = bind(temp, base_contract, base_registry, mutated)
        stale = json.loads(action_path.read_text(encoding="utf-8"))
        stale["contract_id"] = "__wrong_contract__"
        write_json(action_path, stale)
        expect_rejection(
            "I07_WRONG_CONTRACT_ID_REJECTED",
            lambda: load_and_score(
                temp / "contract.json", base_ledger_path, action_path
            ),
            "contract_id 不匹配",
        )

        reversed_actions = copy.deepcopy(base_actions)
        reversed_actions["decisions"].reverse()
        contract_path, action_path, _ = bind(
            temp, base_contract, base_registry, reversed_actions
        )
        reordered = load_and_score(contract_path, base_ledger_path, action_path)
        record(
            "I08_DECISION_ORDER_INVARIANCE",
            same_aggregates(reordered, baseline),
            "aggregate result unchanged under reversed decision order",
        )

        ledger_path = temp / "ledger.csv"
        write_csv(ledger_path, list(reversed(base_rows)))
        contract_path, action_path, _ = bind(
            temp, base_contract, base_registry, base_actions
        )
        row_reordered = load_and_score(contract_path, ledger_path, action_path)
        record(
            "I09_LEDGER_ROW_ORDER_INVARIANCE",
            same_aggregates(row_reordered, baseline),
            "aggregate result unchanged under reversed ledger order",
        )

        write_csv(ledger_path, base_rows[:-1])
        expect_rejection(
            "I10_INCOMPLETE_ROUTE_SET_REJECTED",
            lambda: load_and_score(contract_path, ledger_path, action_path),
            "路线集合不完整",
        )

        duplicate_rows = base_rows + [copy.deepcopy(base_rows[0])]
        write_csv(ledger_path, duplicate_rows)
        expect_rejection(
            "I11_DUPLICATE_LEDGER_KEY_REJECTED",
            lambda: load_and_score(contract_path, ledger_path, action_path),
            "台账键重复",
        )

        mutated_rows = copy.deepcopy(base_rows)
        mutated_rows[0]["effectiveness"] = "nan"
        write_csv(ledger_path, mutated_rows)
        expect_rejection(
            "I12_NONFINITE_LEDGER_REJECTED",
            lambda: load_and_score(contract_path, ledger_path, action_path),
            "非有限数值",
        )

        mutated_rows = copy.deepcopy(base_rows)
        mutated_rows[1]["cost"] = "-0.1"
        write_csv(ledger_path, mutated_rows)
        expect_rejection(
            "I13_NEGATIVE_COST_REJECTED",
            lambda: load_and_score(contract_path, ledger_path, action_path),
            "成本为负数",
        )

        mutated_rows = copy.deepcopy(base_rows)
        mutated_rows[2]["cost"] = "0.10"
        write_csv(ledger_path, mutated_rows)
        expect_rejection(
            "I14_BROKEN_CUMULATIVE_COST_REJECTED",
            lambda: load_and_score(contract_path, ledger_path, action_path),
            "成本并非累计成本",
        )

        broken_registry = copy.deepcopy(base_registry)
        broken_registry["routes"][1]["prerequisites"] = ["__missing__"]
        contract_path, action_path, _ = bind(
            temp, base_contract, broken_registry, base_actions
        )
        write_csv(ledger_path, base_rows)
        expect_rejection(
            "I15_MISSING_PREREQUISITE_REJECTED",
            lambda: load_and_score(contract_path, ledger_path, action_path),
            "未知前置路线",
        )

        cyclic_registry = copy.deepcopy(base_registry)
        cyclic_registry["routes"][0]["prerequisites"] = ["ce20"]
        contract_path, action_path, _ = bind(
            temp, base_contract, cyclic_registry, base_actions
        )
        expect_rejection(
            "I16_PREREQUISITE_CYCLE_REJECTED",
            lambda: load_and_score(contract_path, ledger_path, action_path),
            "前置关系存在环",
        )

        dominated_registry = copy.deepcopy(base_registry)
        dominated_registry["routes"].append(
            {
                "route_id": "dominated",
                "label": "Dominated injected route",
                "prerequisites": ["ce20"],
            }
        )
        dominated_rows = copy.deepcopy(base_rows)
        for query_uid in sorted({row["query_uid"] for row in base_rows}):
            ce_row = next(
                row
                for row in base_rows
                if row["query_uid"] == query_uid and row["route_id"] == "ce20"
            )
            dominated_rows.append(
                {
                    "query_uid": query_uid,
                    "route_id": "dominated",
                    "effectiveness": str(
                        max(float(ce_row["effectiveness"]) - 0.05, 0.0)
                    ),
                    "cost": str(float(ce_row["cost"]) + 0.10),
                }
            )
        contract_path, action_path, _ = bind(
            temp, base_contract, dominated_registry, base_actions
        )
        write_csv(ledger_path, dominated_rows)
        dominated_score = load_and_score(contract_path, ledger_path, action_path)
        record(
            "I17_DOMINATED_ROUTE_INJECTION_INVARIANCE",
            all(
                math.isclose(
                    float(dominated_score[key]),
                    float(baseline[key]),
                    rel_tol=0.0,
                    abs_tol=1e-15,
                )
                for key in invariant_keys[:-1]
            ),
            "oracle and realized aggregates unchanged after dominated route injection",
        )

        duplicate_registry = copy.deepcopy(base_registry)
        duplicate_registry["routes"].append(
            {
                "route_id": "dense_copy",
                "label": "Redundant dense route",
                "prerequisites": ["dense"],
            }
        )
        duplicate_view_rows = copy.deepcopy(base_rows)
        for row in base_rows:
            if row["route_id"] == "dense":
                copy_row = copy.deepcopy(row)
                copy_row["route_id"] = "dense_copy"
                duplicate_view_rows.append(copy_row)
        contract_path, action_path, _ = bind(
            temp, base_contract, duplicate_registry, base_actions
        )
        write_csv(ledger_path, duplicate_view_rows)
        duplicate_score = load_and_score(contract_path, ledger_path, action_path)
        record(
            "I18_REDUNDANT_ROUTE_INJECTION_INVARIANCE",
            all(
                math.isclose(
                    float(duplicate_score[key]),
                    float(baseline[key]),
                    rel_tol=0.0,
                    abs_tol=1e-15,
                )
                for key in invariant_keys[:-1]
            ),
            "registry-order tie break preserves original aggregate result",
        )

    legal_columns = next(
        csv.reader(
            (ROOT / "quickstart" / "participant" / "legal_state.csv").open(
                "r", encoding="utf-8", newline=""
            )
        )
    )
    forbidden = ("qrel", "outcome", "utility", "regret", "oracle", "paid")
    leaked = [
        column
        for column in legal_columns
        if any(token in column.lower() for token in forbidden)
    ]
    record(
        "I19_LEGAL_STATE_COLUMN_SCAN",
        not leaked,
        f"forbidden participant columns={leaked}",
    )

    failed = [probe for probe in probes if probe["status"] != "pass"]
    report = {
        "suite_id": "worthir-integrity-v1",
        "status": "PASS" if not failed else "FAIL",
        "summary": {
            "probes": len(probes),
            "passed": len(probes) - len(failed),
            "failed": len(failed),
        },
        "probes": probes,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], **report["summary"]}, indent=2))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()

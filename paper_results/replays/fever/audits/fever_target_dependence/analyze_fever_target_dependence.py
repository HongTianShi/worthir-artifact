#!/usr/bin/env python3
"""Frozen-outcome FEVER target and dependence sensitivity.

This script never fits or selects an adaptive learner. It rescales the already
frozen action vectors against an alternative, verification-grounded target and
audits the archived NDCG contrast with a dependence unit induced by shared gold
evidence pages or identical normalized claims.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROUTES = ("bm25", "bi200", "ce20", "ce100", "hybrid")
LAMBDAS = (0.0, 0.02, 0.04, 0.08, 0.16)
SEED = 20260731


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = np.arange(n, dtype=np.int64)
        self.size = np.ones(n, dtype=np.int64)

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = int(self.parent[x])
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


def load_actions(path: Path) -> pd.DataFrame:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    out = pd.DataFrame(rows)
    if out["query_uid"].duplicated().any():
        raise SystemExit("duplicate action query_uid")
    return out


def build_components(
    membership: pd.DataFrame, qrels: pd.DataFrame
) -> tuple[pd.DataFrame, dict]:
    ids = membership["query_uid"].astype(str).tolist()
    pos = {q: i for i, q in enumerate(ids)}
    uf = UnionFind(len(ids))

    for _, g in qrels[qrels["query_uid"].isin(pos)].groupby("doc_id", sort=False):
        members = [pos[q] for q in g["query_uid"].astype(str).unique()]
        if len(members) > 1:
            first = members[0]
            for other in members[1:]:
                uf.union(first, other)

    for _, g in membership.groupby("claim_normalized", sort=False):
        members = [pos[q] for q in g["query_uid"].astype(str)]
        if len(members) > 1:
            first = members[0]
            for other in members[1:]:
                uf.union(first, other)

    roots = np.array([uf.find(i) for i in range(len(ids))], dtype=np.int64)
    unique_roots, labels = np.unique(roots, return_inverse=True)
    comp = pd.DataFrame(
        {
            "query_uid": ids,
            "component_id": [f"fever_dep_{x:05d}" for x in labels],
        }
    )
    counts = pd.Series(labels).value_counts().sort_values(ascending=False)
    summary = {
        "definition": "connected components induced by shared gold evidence page or identical normalized claim",
        "queries": len(ids),
        "components": int(len(unique_roots)),
        "largest_component": int(counts.iloc[0]),
        "singleton_components": int((counts == 1).sum()),
        "components_ge_10": int((counts >= 10).sum()),
        "p50_component_size": float(counts.quantile(0.50)),
        "p90_component_size": float(counts.quantile(0.90)),
        "p99_component_size": float(counts.quantile(0.99)),
    }
    return comp, summary


def bootstrap_ranges(
    diff: np.ndarray,
    labels: np.ndarray,
    rng: np.random.Generator,
    draws: int,
) -> dict:
    unique, inverse = np.unique(labels, return_inverse=True)
    sums = np.bincount(inverse, weights=diff)
    counts = np.bincount(inverse)
    group_n = len(unique)

    cluster = np.empty(draws, dtype=np.float64)
    query = np.empty(draws, dtype=np.float64)
    n = len(diff)
    for b in range(draws):
        chosen = rng.integers(0, group_n, size=group_n)
        cluster[b] = sums[chosen].sum() / counts[chosen].sum()
        qidx = rng.integers(0, n, size=n)
        query[b] = diff[qidx].mean()

    total_sum = float(diff.sum())
    total_n = len(diff)
    loo = (total_sum - sums) / (total_n - counts)
    return {
        "mean": float(diff.mean()),
        "query_bootstrap_q025_q975": [
            float(np.quantile(query, 0.025)),
            float(np.quantile(query, 0.975)),
        ],
        "shared_page_component_bootstrap_q025_q975": [
            float(np.quantile(cluster, 0.025)),
            float(np.quantile(cluster, 0.975)),
        ],
        "leave_one_component_out_min_max": [float(loo.min()), float(loo.max())],
        "positive_component_bootstrap_fraction": float((cluster > 0).mean()),
    }


def evaluate_metric(
    metric: str,
    dev_out: pd.DataFrame,
    test_out: pd.DataFrame,
    costs: pd.DataFrame,
    actions: pd.DataFrame,
    comp: pd.DataFrame,
    draws: int,
) -> list[dict]:
    dev_ids = set(dev_out["query_uid"])
    test_ids = set(test_out["query_uid"])
    dev_cost = costs[costs["query_uid"].isin(dev_ids)]
    test_cost = costs[costs["query_uid"].isin(test_ids)]

    dev_q = dev_out.pivot(index="query_uid", columns="route", values=metric)[list(ROUTES)]
    test_q = test_out.pivot(index="query_uid", columns="route", values=metric)[list(ROUTES)]
    dev_c = dev_cost.pivot(index="query_uid", columns="route", values="cost_work")[list(ROUTES)]
    test_c = test_cost.pivot(index="query_uid", columns="route", values="cost_work")[list(ROUTES)]
    actions_i = actions.set_index("query_uid").loc[test_q.index]
    labels = comp.set_index("query_uid").loc[test_q.index, "component_id"].to_numpy()
    rng = np.random.default_rng(SEED + (0 if metric == "raw_ndcg_10" else 1000))

    records = []
    for lam in LAMBDAS:
        dev_u = dev_q - lam * dev_c
        test_u = test_q - lam * test_c
        f_dev_route = str(dev_u.mean().idxmax())
        f_tih_route = str(test_u.mean().idxmax())
        action_col = f"adaptive_lambda_{lam}"
        selected = actions_i[action_col].astype(str).to_numpy()
        row_idx = np.arange(len(test_u))
        route_pos = {r: i for i, r in enumerate(ROUTES)}
        selected_pos = np.array([route_pos[r] for r in selected], dtype=np.int64)
        values = test_u.to_numpy()
        a = values[row_idx, selected_pos]
        f_dev = values[:, route_pos[f_dev_route]]
        f_tih = values[:, route_pos[f_tih_route]]
        oracle = values.max(axis=1)
        delta_dev = a - f_dev
        delta_tih = a - f_tih
        headroom_dev = float(oracle.mean() - f_dev.mean())
        headroom_tih = float(oracle.mean() - f_tih.mean())
        records.append(
            {
                "metric": metric,
                "lambda": lam,
                "policy_status": "same frozen NDCG-trained legal action vector; no refitting",
                "F_dev_route": f_dev_route,
                "F_TIH_route": f_tih_route,
                "F_dev": float(f_dev.mean()),
                "F_TIH": float(f_tih.mean()),
                "A_frozen": float(a.mean()),
                "O_TIH": float(oracle.mean()),
                "delta_dev": float(delta_dev.mean()),
                "delta_tih": float(delta_tih.mean()),
                "headroom_dev": headroom_dev,
                "headroom_tih": headroom_tih,
                "kappa_dev": float(delta_dev.mean() / headroom_dev)
                if headroom_dev > 0
                else None,
                "kappa_tih": float(delta_tih.mean() / headroom_tih)
                if headroom_tih > 0
                else None,
                "delta_dev_resampling": bootstrap_ranges(
                    delta_dev, labels, rng, draws
                ),
                "delta_tih_resampling": bootstrap_ranges(
                    delta_tih, labels, rng, draws
                ),
            }
        )
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-outcomes", type=Path, required=True)
    ap.add_argument("--development-outcomes", type=Path, required=True)
    ap.add_argument("--costs", type=Path, required=True)
    ap.add_argument("--actions", type=Path, required=True)
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--qrels", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--draws", type=int, default=5000)
    args = ap.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    test_out = pd.read_parquet(args.test_outcomes)
    dev_out = pd.read_parquet(args.development_outcomes)
    costs = pd.read_parquet(args.costs)
    actions = load_actions(args.actions)
    membership = pd.read_parquet(args.membership)
    qrels = pd.read_parquet(args.qrels)

    if len(membership) != 13332 or membership["query_uid"].duplicated().any():
        raise SystemExit("unexpected test membership")
    if len(test_out) != 13332 * len(ROUTES):
        raise SystemExit("incomplete test outcome matrix")
    if len(dev_out) != 6000 * len(ROUTES):
        raise SystemExit("incomplete development outcome matrix")
    if len(actions) != 13332:
        raise SystemExit("incomplete action vector")

    comp, comp_summary = build_components(membership, qrels)
    comp.to_csv(args.output_dir / "fever_dependency_components.csv", index=False)

    results = []
    for metric in ("raw_ndcg_10", "complete_set_recall_10"):
        results.extend(
            evaluate_metric(
                metric, dev_out, test_out, costs, actions, comp, args.draws
            )
        )

    payload = {
        "schema_version": "worthir-fever-target-dependence-sensitivity-v1.0",
        "status": "complete",
        "scope": "frozen-outcome rescoring only; no model fit, selection, or route rerun",
        "seed": SEED,
        "draws": args.draws,
        "component_summary": comp_summary,
        "results": results,
    }
    json_path = args.output_dir / "FEVER_TARGET_DEPENDENCE_SENSITIVITY.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    flat_rows = []
    for r in results:
        flat_rows.append(
            {
                "metric": r["metric"],
                "lambda": r["lambda"],
                "F_dev_route": r["F_dev_route"],
                "F_TIH_route": r["F_TIH_route"],
                "F_dev": r["F_dev"],
                "F_TIH": r["F_TIH"],
                "A_frozen": r["A_frozen"],
                "O_TIH": r["O_TIH"],
                "delta_dev": r["delta_dev"],
                "delta_tih": r["delta_tih"],
                "kappa_dev": r["kappa_dev"],
                "component_q025": r["delta_dev_resampling"][
                    "shared_page_component_bootstrap_q025_q975"
                ][0],
                "component_q975": r["delta_dev_resampling"][
                    "shared_page_component_bootstrap_q025_q975"
                ][1],
                "loo_min": r["delta_dev_resampling"][
                    "leave_one_component_out_min_max"
                ][0],
                "loo_max": r["delta_dev_resampling"][
                    "leave_one_component_out_min_max"
                ][1],
            }
        )
    pd.DataFrame(flat_rows).to_csv(
        args.output_dir / "fever_target_sensitivity.csv", index=False
    )

    def find(metric: str, lam: float) -> dict:
        return next(
            r for r in results if r["metric"] == metric and r["lambda"] == lam
        )

    ndcg = find("raw_ndcg_10", 0.08)
    complete = find("complete_set_recall_10", 0.08)
    md = f"""# FEVER target and dependence sensitivity

Decision: **PASS as a frozen-outcome sensitivity.**

No route was rerun and no learner was fitted or selected. The registered
NDCG-trained legal action vectors were rescored against the archived complete
evidence-set success indicator.

## Dependence unit

- Queries: {comp_summary['queries']:,}
- Components: {comp_summary['components']:,}
- Largest component: {comp_summary['largest_component']:,}
- Singleton components: {comp_summary['singleton_components']:,}
- Definition: {comp_summary['definition']}.

At lambda .08, the archived NDCG utility contrast is
{ndcg['delta_dev']:.6f}. Its shared-page component-resampling range is
[{ndcg['delta_dev_resampling']['shared_page_component_bootstrap_q025_q975'][0]:.6f},
 {ndcg['delta_dev_resampling']['shared_page_component_bootstrap_q025_q975'][1]:.6f}],
and its leave-one-component-out range is
[{ndcg['delta_dev_resampling']['leave_one_component_out_min_max'][0]:.6f},
 {ndcg['delta_dev_resampling']['leave_one_component_out_min_max'][1]:.6f}].

## Verification-grounded target

Complete-set recall@10 equals one only when the ranking contains every page
from at least one valid official evidence set. At lambda .08:

- development-selected fixed route: {complete['F_dev_route']};
- test-hindsight fixed route: {complete['F_TIH_route']};
- fixed utility: {complete['F_dev']:.6f};
- frozen legal-policy utility: {complete['A_frozen']:.6f};
- evaluator oracle utility: {complete['O_TIH']:.6f};
- legal-policy gain: {complete['delta_dev']:.6f};
- headroom recovered: {100 * complete['kappa_dev']:.2f}%;
- shared-page component-resampling range:
  [{complete['delta_dev_resampling']['shared_page_component_bootstrap_q025_q975'][0]:.6f},
   {complete['delta_dev_resampling']['shared_page_component_bootstrap_q025_q975'][1]:.6f}].

## Claim policy

**Strongest defensible.** The positive FEVER acquisition result survives both
a verification-grounded complete-evidence-set target and resampling over
shared-gold-page dependence components.

**Conservative fallback.** The frozen NDCG-trained action vector retains
positive finite-ledger utility when rescored for complete evidence-set
success.

**Prohibited.** Population coverage, independence of FEVER claims, prospective
confirmation, or an official end-to-end FEVER verification score.
"""
    (args.output_dir / "FEVER_TARGET_DEPENDENCE_SENSITIVITY.md").write_text(
        md, encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "json": str(json_path)}, indent=2))


if __name__ == "__main__":
    main()

# WorthIR--FEVER full validation report

Date: 2026-07-31  
Decision: **PASS**

## Scope

This report validates the completed retrospective, outcome-separated FEVER
task. It does not treat FEVER as prospective evidence and does not alter the
registered policy, route menu, costs, metrics, population, or thresholds.

## Population and execution

- Development population: 6,000 unique official-train claims.
- Outcome-separated test population: all 13,332 verifiable official
  shared-task-development claims.
- Corpus: 5,416,537 official FEVER Wikipedia pages.
- Routes: BM25, bi-encoder reranking of up to 200 candidates, cross-encoder
  reranking at depths 20 and 100, and bi-encoder--cross-encoder hybrid.
- Full route ledger: 19,332 unique queries x five routes.
- GPU execution: NVIDIA GeForce RTX 4070 Laptop GPU, PyTorch 2.9.0+cu126.

## Independent validator

`validate_full_bundle.py` passed **63/63** checks. The checks cover:

1. exact and disjoint development/test memberships;
2. complete and unique query--route matrices;
3. finite metrics and operator costs;
4. legal-state leakage exclusion by field and lineage;
5. registered route completeness and route-ledger hashing;
6. development-only policy selection;
7. action freezing before official-development-test outcome materialization;
8. fixed-reference invariance;
9. binding hashes for legal state, costs, actions, outcomes, and evaluation;
10. complete preference-grid reporting;
11. evaluator-oracle dominance sanity checks; and
12. byte/state identity of the registered replay inputs.

Machine-readable results:
`reports/full_validation_results.json`.

## Temporal validity

The paid-route execution consumed no qrels. Development outcomes were joined
first and were the only outcomes available to model-family selection and
refitting. The 13,332 test actions were written and hashed before test
outcomes were materialized. Test scoring then joined the frozen route ledger
to official evidence pages. `F_dev` is query-invariant; `A_dev` consumes only
the claim-form and BM25 score-shape legal state plus the declared menu cost.

## Target validity

- Only `SUPPORTS` and `REFUTES` claims with at least one complete,
  sentence-valid official evidence set are included.
- Page qrels are the union of pages belonging to a valid complete evidence
  set.
- All 14,533 required page identifiers resolve uniquely to the frozen Lucene
  index; 3,114 require the registered exact FEVER escape decoding.
- Three normalized claim overlaps between official train and development were
  excluded from development.
- Primary `NDCG@10`, secondary `Recall@10`, and complete-set recall are finite
  in `[0,1]` for all query--route pairs.

## Cost validity

The primary profile is qrel-independent operator-counted tokenizer work,
computed from actual non-padding tokens and preserving cumulative route
dependencies. The common BM25 parent has zero incremental within-menu cost.

The secondary hardware-qualified profile uses 200 deterministically selected
queries and real warm execution on the registered RTX 4070. Adding the common
BM25 parent gives median cumulative latencies of:

| Route | Median cumulative latency (ms) | Test NDCG@10 |
|---|---:|---:|
| BM25 | 22.04 | 0.6602 |
| CE-20 | 74.65 | 0.7832 |
| bi-200 | 277.96 | 0.6133 |
| CE-100 | 283.67 | 0.8156 |
| Hybrid | 325.40 | 0.7796 |

For mean, median, and p95 latency, the same fixed-view frontier is
`BM25 -> CE-20 -> CE-100`; bi-200 and hybrid are dominated. This is a
hardware-qualified descriptive frontier, not a universal latency claim.

## Replay-input integrity

The before and after state records were exactly equal. Scientific replay
inputs are bound by the artifact manifest.

## Final validation decision

The FEVER bundle is complete, role-separated, hash-bound, and suitable for
scientific interpretation under its registered retrospective scope.

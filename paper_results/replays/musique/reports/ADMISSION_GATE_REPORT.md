# MuSiQue-WorthIR admission gate

**Decision: FULL PASS.**

The gate evaluates the preregistered four-route, paragraph-ID task on all 2,417 answerable official-validation queries. No threshold, route, cost, learner, or membership was changed after outcome materialization.

## Gate results

| Gate | Result | Key evidence |
|---|---:|---|
| G0 integrity | PASS | 89,420 complete rankings; 0 ranking and 0 metric errors; frozen inputs changed: 0 |
| G1 heterogeneity | PASS | 4 raw-share routes, 2 utility-share routes; top-1 disagreement 68.23% |
| G2 headroom | PASS | utility 0.123745 [0.116910, 0.130725]; raw 0.116081 |
| G3 breadth | PASS | strongest fixed NDCG 0.527636; 6/6 hop strata above .04 |
| G4 recoverability | PASS | A_dev-F_dev 0.013970 [0.006425, 0.021461]; kappa 11.29% |
| G5 controls | PASS | V2-shuffle 0.353732; V3-wrong-decomposition 0.076853 |

## References

- F_dev: V2; utility 0.505436.
- F_TIH: V2; utility 0.505436.
- A_dev (extra_trees): utility 0.519406.
- O_TIH: utility 0.629182.

## Claim boundary

**Strongest defensible claim.** MuSiQue supplies an independently split structured retrieval surface with a complete, heterogeneous route menu, substantial per-query decision headroom, and faithfully detected paragraph/decomposition signal under the registered controls.

**Conservative fallback.** The surface is a same-family replication of structured evidence acquisition, not an orthogonal document-retrieval family; its legal state assumes released decomposition questions.

**Prohibited claim.** This gate cannot establish universal recoverability, causal benefit from graph structure, or prospective deployment from raw questions without decomposition.

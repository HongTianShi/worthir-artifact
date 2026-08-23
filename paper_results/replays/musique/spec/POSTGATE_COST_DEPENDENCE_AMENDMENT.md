# MuSiQue post-gate cost and dependence amendment

Status: append-only post-gate robustness record. The registered task,
membership, routes, official-validation actions, thresholds, and primary
relative-effort result remain unchanged.

## Evidence status

The original lock is hash-bound and was written before official-validation
route outcomes were materialized, but it has no independent third-party
timestamp. The correct label is therefore **workflow-frozen retrospective
outcome-separated evaluation**, not externally witnessed preregistration or
prospective confirmation.

## Query-conditioned cost

MuSiQue uses costs known from legal query structure before commitment. The
general contract is \(C_\pi(q,v)\). A route-level schedule \(C_\pi(v)\) is the
special case that is constant across queries.

The registered `relative_v1` profile divides each query's route work by that
query's V3 work:

- V0: \(0\)
- V1: \(d_q T_q\)
- V2: \(P_q\)
- V3: \(d_qT_q+(1+d_q)P_q\)

This produces a dimensionless within-query relative-effort fraction. It is
not additive across queries and is not latency, energy, money, or an absolute
amount of computation.

The post-gate `common_devmean_v1` profile divides the same raw work by the
mean V3 work on the development split (5829.989970 token-scoring units).
This denominator is fixed without official-validation outcomes and creates a
common additive work unit across queries. Model fitting, development
selection, fixed-reference selection, and official-validation scoring were
rerun under this profile.

Released decomposition questions are conditional legal state in both
profiles. Their route-specific scoring work is charged; the upstream human
annotation cost that created the released decomposition is outside the
execution boundary and remains an external-validity limitation.

## Dependence-aware uncertainty

The exact mean over all 2,417 answerable official-validation queries remains
the primary finite-ledger estimand. Resampling intervals are conditional
stability diagnostics, not query-superpopulation coverage.

Queries are connected when they share an exact normalized gold support title,
an exact gold support-paragraph text hash, or an exact normalized released
decomposition question. The strict union graph contains 179 components and a
1,437-query giant component. Component bootstraps are reported alongside the
ordinary query bootstrap, and every dependence key and component membership
is retained in `official_validation_components.parquet`.

## Reproducibility

- `postgate_common_cost_dependence.py` applies the same component audit to
  the common-denominator result.
- `score_action_file.py` validates one registered route per test query and
  joins outcomes only after action validation.

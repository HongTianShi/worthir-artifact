# WorthIR--FEVER full-run authorization

Date: 2026-07-30  
Status: **authorized and frozen before full-test outcomes**

The preregistered 1,200-query pilot returned `PROCEED_TO_FULL`.  All four
integrity gates and all four scientific admission gates passed.  The exact
decision is stored in `pilot/PILOT_GATE_DECISION.json`.

## Frozen full populations

- Policy development: 6,000 unique normalized claim groups sampled from
  official FEVER train, excluding all normalized overlaps with official
  shared-task development.
- Outcome-separated test: all 13,332 verifiable official shared-task
  development claims.
- Routes, corpus, candidate depth, checkpoints, metrics, costs, lambda grid,
  tie rules, and legal-state fields are unchanged from task v1.0.

## Full policy selection

`F_dev` selects one fixed route on all 6,000 development queries for each
registered lambda and is then frozen.

The adaptive measurement probe predicts the five route raw NDCG values from
the registered legal state.  Candidate families are RF and ExtraTrees with
300 trees, `max_features=.7`, `min_samples_leaf` in `{5,20}`, seed 20260730.
Configuration selection uses deterministic five-fold claim-hash
cross-validation on the 6,000 development queries and headline
`lambda=.08`.  The selected configuration is refit on all 6,000 queries.
Costs are subtracted only after raw-quality prediction and are not predictor
features.  The resulting test action file is hashed before full-test qrels
are joined.

## Full readouts

The full report must retain, for every registered lambda:

- `F_dev`, `F_TIH`, `A_dev`, and `O_TIH`;
- deployable and conservative paired intervals;
- absolute oracle headroom and empirical recoverability;
- fixed, adaptive, and oracle action shares;
- raw quality, complete-set recall, operator-counted cost, and quality--cost
  frontier.

The report also retains the unfavorable results.  No full-run result is a
gate for redesigning or deleting a route.  This task is retrospective and
outcome-separated, not prospective.


# Canonical WorthIR Evaluation Outputs

The task preserves the complete query–route outcome ledger and exposes several
decision views. No single output should be presented as the only legitimate
summary.

## Primary report

The frozen primary criterion is:

`U = NDCG@10 - 0.08 C_op`.

For each held-out year, the scorer returns the submitted policy's mean quality,
mean cost under all registered profiles, primary utility, exact within-menu
regret, oracle-match rate, purchase-error counts, and deterministic
query-bootstrap intervals. TREC DL 2019 and 2020 remain separate.

## Preference sensitivity

The same committed decisions are rescored under:

- `C_op`, `C_lat`, and `C_mem`;
- `lambda` in `{0, .04, .08, .16, .32}`.

This is frozen-outcome sensitivity. It is not policy retraining or
test-conditioned route selection.

## Pairwise comparison

`worthir-eval compare` aligns two submissions by `query_uid` and reports paired
quality, cost, and primary-utility differences with deterministic bootstrap
intervals. It does not pool the two TREC years.

## Pareto and hard-budget views

`worthir-eval frontier` accepts two or more already committed submissions and,
for each year and cost profile:

- reports their mean quality–cost operating points;
- marks Pareto-nondominated submissions;
- selects the highest-quality feasible submission at declared normalized
  budgets.

This view prevents the linear utility from becoming an undeclared universal
preference. The primary utility remains the frozen headline criterion; Pareto
and hard-budget outputs expose how a conclusion changes under other declared
preferences.

## Privacy boundary

Participant-facing score files contain aggregates only. They never include
query IDs, qrels, per-query route outcomes, per-query oracle routes, or
per-query regret. Organizer-side raw rankings, qrels, candidate fingerprints,
and dependency fingerprints are retained solely for independent replay.


# WorthIR TREC-DL Multi-Stage Task v1.0

## Identity

- Task ID: `worthir-trecdl-multistage-v1.0`
- Evaluation object: a route purchase committed before paid-route execution
  outcomes or relevance judgments are visible.
- Unit of decision: one eligible query.
- Action space: four frozen compiled retrieval routes.
- Intended use: train on the public development ledger, then submit one legal
  route per held-out TREC DL query.
- Non-goal: ranking-document submission, route construction, model training,
  or a claim that cost-aware selection must change the fixed winner.

## Decision timeline

1. The participant observes the query, legal BM25 output, query-only
   descriptors, route descriptors, declared parent closure, and cost profiles.
2. The participant commits to exactly one registered route.
3. The evaluator joins the committed route to the hidden complete-menu
   outcome ledger.
4. The evaluator reports chosen quality and cost, primary and sensitivity
   utilities, and exact within-menu regret.

No field derived from qrels, paid-route candidates/scores, route quality,
utility, regret, oracle action, or a test-selected policy is legal at step 1.

## Populations

Development uses all 6,980 MS MARCO passage `dev/small` queries with at least
one official positive judgment. Test uses all eligible judged topics from
TREC DL 2019 (43) and 2020 (54). The three query-UID sets are disjoint.
No topic is discarded based on route behavior.

## Menu and dependencies

The authoritative route order is:

`stop_bm25`, `dense_fusion`, `late_interaction`, `cross_encoder`.

`dense_fusion` depends on the legal BM25 base plus exact dense retrieval.
`late_interaction` and `cross_encoder` independently depend on
`dense_fusion`; neither is a child of the other. Reranked prefixes retain the
untouched parent tail. The participant selects a compiled route, so the
evaluator charges its complete registered dependency closure.

## Metric and cost

The hidden quality target is official judged NDCG@10. Costs are frozen
route-level development measurements:

- `C_op`: parent-aware operator proxy, primary;
- `C_lat`: prepared-input warm operator latency, secondary;
- `C_mem`: provisioned incremental footprint, secondary.

BM25 is common pre-purchase state: its raw systems cost is reported but its
incremental decision charge is zero. The primary profile is
`U = A - .08 C_op`. Registered sensitivity lambdas are
`0, .04, .08, .16, .32`.

## Submission

A submission is one JSON document with:

- `schema_id`;
- `task_id`;
- a nonempty `policy_id`;
- exactly one `{query_uid, selected_route_id}` decision for every query in
  both held-out tracks.

Unknown, missing, extra, or duplicate queries; unknown routes; extra decision
fields and non-string identifiers are rejected before
scoring.

## Reporting

The evaluator reports 2019 and 2020 separately. Each track includes:

- mean raw NDCG@10;
- mean costs under all three frozen profiles;
- primary utility and exact regret;
- sensitivity utility/regret grid;
- regret quantiles and oracle-match rate;
- purchase-error taxonomy;
- deterministic query-bootstrap intervals for primary utility and regret.

The evaluator may provide a descriptive two-track vector but must not pool the
confirmatory years into a single inferential claim.

## Evidence status

This release operationalizes an already completed and preregistered G2 task.
The held-out results have been accessed and independently validated; package
construction is therefore retrospective task engineering, not a new sealed
experiment. Any future method comparison must make a fresh train/dev/test
selection declaration before requesting held-out scores.

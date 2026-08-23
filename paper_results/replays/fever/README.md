# FEVER replay

This package evaluates five routes over 13,332 FEVER claims using page-level
NDCG@10 and cumulative transformer-token work.

## Information boundary

`participant/legal_state.parquet` contains query IDs, evaluation role, claim
form counts, and BM25 score-shape features. It excludes claim text, qrels,
evidence IDs, paid-route outcomes, utilities, and oracle actions.

`organizer_private/` contains the complete five-route effectiveness/cost
matrix used only after actions are fixed.

## Score an action file

```bash
python scripts/make_action_template.py --output actions.csv
python scripts/score_actions.py \
  --actions actions.csv \
  --lambda-value 0.08 \
  --output score.json
```

Registered routes are `bm25`, `bi200`, `ce20`, `ce100`, and `hybrid`.
`frozen_results/` contains the released actions and aggregate results;
`audits/` contains dependence and target-sensitivity checks; `spec/` defines
the execution and latency protocols.

The Wikipedia snapshot, index, checkpoints, and candidate cache are not
distributed. Verify bundle integrity with `python scripts/verify_bundle.py
--bundle-root .`.

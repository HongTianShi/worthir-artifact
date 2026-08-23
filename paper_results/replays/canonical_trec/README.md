# TREC-DL replay

- `public/`: action-time state, contracts, route registry, and reference
  actions.
- `organizer_private/`: compact route outcomes used by the evaluator after
actions are fixed.

Run `score_actions.py` to score a reference action file.

Policies may use only the public surface. The evaluator ledger is distributed
to reproduce the completed task but remains invalid as policy input.

The package omits the MS MARCO development tables, raw TREC qrels, full route
rankings, and detailed candidate audits. They are unnecessary for aggregate
scoring. See `public/docs/DATA_ACCESS_NOTICE.md` and
`../../full_replay/CANONICAL_TREC.md`.

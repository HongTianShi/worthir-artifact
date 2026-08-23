# TREC-DL raw reconstruction

The compact package under `replays/canonical_trec/` is sufficient for action
scoring and aggregate result reproduction. Raw route reconstruction additionally
requires the MS MARCO passage collection, TREC-DL 2019/2020 topics and qrels,
the named Pyserini indexes, and the registered reranking checkpoints.

Preserve the route order and cumulative parent costs defined in
`public/contracts/route_registry.json` and `cost_contract.json`.

# FiQA260 diagnostics

This package joins 260 stable FiQA query IDs to eight NDCG@10 routes:
`summary`, `binary`, `pq`, `int8`, `hnsw16`, `hnsw64`, `full`, and `ce`.

- `query_membership.parquet`: identifiers and provenance key.
- `legal_state.parquet`: action-time fields.
- `raw_quality_labels.parquet`: evaluator-side effectiveness.
- `execution_fingerprints.parquet`: route execution commitments.
- `candidate_pool_fingerprints.parquet`: candidate-pool commitments.

Reproduce the diagnostic figures and checks from the repository root:

```bash
python scripts/reproduce_paper.py --output-dir reproduced/paper
```

Candidate lists, scores, upstream corpus, and model checkpoints are not
included.

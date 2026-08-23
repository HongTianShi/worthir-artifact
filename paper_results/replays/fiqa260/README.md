# FiQA260 诊断

该软件包将 260 个稳定 FiQA 查询 ID 与 8 条 NDCG@10 路线关联：
`summary`、`binary`、`pq`、`int8`、`hnsw16`、`hnsw64`、`full` 和 `ce`。

- `query_membership.parquet`：标识符和来源键。
- `legal_state.parquet`：动作时可用字段。
- `raw_quality_labels.parquet`：评测端有效性。
- `execution_fingerprints.parquet`：路线执行约定。
- `candidate_pool_fingerprints.parquet`：候选池约定。

从仓库根目录复现诊断图和检查：

```bash
python scripts/reproduce_paper.py --output-dir reproduced/paper
```

仓库不包含候选列表、分数、上游语料库或模型检查点。

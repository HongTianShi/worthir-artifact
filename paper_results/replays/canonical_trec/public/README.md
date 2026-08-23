# TREC-DL 回放

在 `public/reference_submissions/` 下的文件中为每个 topic 选择一条路线，然后运行：

```bash
python score_actions.py \
  --actions public/reference_submissions/stop_bm25.json \
  --output score.json
```

可用路线为 `stop_bm25`、`dense_fusion`、`late_interaction` 和
`cross_encoder`。输出分别报告 2019 和 2020 的 NDCG@10、成本、效用和遗憾。

仓库不分发原始 qrels、完整排名或 MS MARCO 开发表。

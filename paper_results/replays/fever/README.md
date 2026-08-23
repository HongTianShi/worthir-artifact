# FEVER 回放

该软件包使用页面级 NDCG@10 和累计 Transformer token 工作量，在 13,332 条
FEVER claim 上评估 5 条路线。

## 信息边界

`participant/legal_state.parquet` 包含查询 ID、评测角色、claim 形式计数和 BM25
分数形态特征，不包含 claim 文本、qrels、证据 ID、付费路线结果、效用或 Oracle 动作。

`organizer_private/` 包含完整的 5 路线有效性/成本矩阵，仅在动作冻结后使用。

## 评估动作文件

```bash
python scripts/make_action_template.py --output actions.csv
python scripts/score_actions.py \
  --actions actions.csv \
  --lambda-value 0.08 \
  --output score.json
```

已注册路线为 `bm25`、`bi200`、`ce20`、`ce100` 和 `hybrid`。
`frozen_results/` 包含已发布动作和汇总结果；`audits/` 包含依赖性和目标敏感性检查；
`spec/` 定义执行及延迟协议。

仓库不分发 Wikipedia 快照、索引、检查点或候选缓存。可运行
`python scripts/verify_bundle.py --bundle-root .` 验证软件包结构。

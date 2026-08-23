# FEVER 重建卡

已发布评分接口位于 `replays/fever/`，包含合法状态、冻结动作、完整的已发布 5 路线
ledger、操作工作量成本、带硬件说明的延迟报告和失败即拒绝的评分器。

原始重建还需要官方 FEVER 2017 Wikipedia dump、对应页面索引、`bi200`、`ce20`、
`ce100` 和 `hybrid` 使用的检查点以及候选缓存。每条路线必须对同一 5,416,537 页面
语料库排名。主要成本是公共 BM25 父路线之后实际处理的非 padding Transformer token
工作量；RTX 4070 Laptop 预热延迟是带硬件条件的次要设定。

已发布动作回放命令为：

```text
python replays/fever/scripts/score_actions.py \
  --bundle-root replays/fever \
  --actions replays/fever/frozen_results/registered_actions_lambda08.csv \
  --lambda-value 0.08 \
  --output reproduced/fever_score.json
```

该命令评估冻结结果，并不声称重新运行 540 万页面检索管线。

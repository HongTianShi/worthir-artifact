# 论文复现输入依据

| 结果 | 输入 | 验证层级 |
| --- | --- | --- |
| 图 1 | `../figures/hero_example_2019.json` 及绑定的 TREC 资产 | 包含文件和记录来源的冻结诊断示例 |
| 图 2 | `../figures/cost_quality_inversion_data.csv` | 坐标和来源验证 |
| 图 3 | `../figures/recoverability_bridge_data.csv` | 任务内归一化绘图坐标 |
| 表 2 | `replays/canonical_trec/organizer_private/data/test/*/route_outcomes.parquet` | 根据完整逐查询路线 ledger 和论文使用的并列感知有效性 Oracle 规则重新计算 |
| 表 3 | `table3_recoverability.csv` | 增益和剩余空间的算术恒等式；如有发布则采用原生动作评分 |
| 表 4 | `table4_query_level.parquet` | 根据 12,000 条冻结查询记录重新汇总 |

早期探索性 TREC 任务健康度 JSON 使用了朴素的首次 argmax 并列处理，因此有意排除。
不得用它计算论文中的 13/43 和 14/54 分歧数量。

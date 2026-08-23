# 论文结果索引

先在本目录运行 `python run.py`。下表中的输出都会保留在 `reproduced/` 下。

| 论文项目 | 发布输入 | 生成或校验程序 | 持久化输出 | 复现层级 |
| --- | --- | --- | --- | --- |
| Figure 1 | `paper_reproduction/figures/hero_example_2019.json` | `scripts/reproduce_paper.py` | `reproduced/paper/figures/figure1.pdf` | 完整重绘 |
| Figure 2 | `paper_reproduction/figures/cost_quality_inversion_data.csv` | `scripts/reproduce_paper.py` | `reproduced/paper/figures/cost_quality_final.png` | 完整重绘 |
| Figure 3 | `paper_reproduction/figures/recoverability_bridge_data.csv` | `scripts/reproduce_paper.py` | `reproduced/paper/figures/recoverability_bridge.png` | 完整重绘 |
| Figure 4 | `analyses/rq3_utility_sources/data/query_strata.csv` | `scripts/reproduce_rqs.py` | `reproduced/rqs/rq3_query_strata.csv` | 数值闭合，不重绘最终图片 |
| Figure 5 | `analyses/rq4_robustness/data/cost_preference_summary.csv` | `scripts/reproduce_rqs.py` | `reproduced/rqs/rq4_cost_preference.csv` | 数值闭合，不重绘最终图片 |
| Figure 6 | `analyses/rq5_route_value/data/rq5_fever_gold_rank_band_routes.csv` | `scripts/reproduce_rqs.py` 中的 RQ5 校验 | `reproduced/rqs/reproduction_report.json` | 校验源表，不重绘最终图片 |
| Figure 7 | `analyses/rq2_policy_comparison/results/fever_online_latency.csv` | `scripts/reproduce_rqs.py` 中的 RQ2 校验 | `reproduced/rqs/reproduction_report.json` | 校验源表，不重绘最终图片 |
| Table 2 | 完整 TREC-DL 路线台账 | `scripts/reproduce_paper.py` | `reproduced/paper/table2_canonical_heldout.csv` | 逐查询重算 |
| Table 3 | `paper_reproduction/inputs/table3_recoverability.csv` | `scripts/reproduce_paper.py` | `reproduced/paper/table3_recoverability.csv` | 算术重算 |
| Table 4 | `paper_reproduction/inputs/table4_query_level.parquet` | `scripts/reproduce_paper.py` | `reproduced/paper/table4_matched_top10.csv` | 逐查询重新汇总 |
| Table 5 | `analyses/rq2_policy_comparison/results/fever_same_menu_policy_comparison.csv` | `scripts/reproduce_rqs.py` | `reproduced/rqs/rq2_fever_same_menu.csv` | 重新评分并校验表格 |
| Table 6 | `analyses/rq5_route_value/data/rq5_route_value_prediction_summary.csv` | `scripts/reproduce_rqs.py` 中的 RQ5 校验 | `reproduced/rqs/rq5_prediction_summary.csv` | 根据发布预测结果做数值闭合 |

## 附录结果

| 结果类别 | 仓库位置 | 本地可运行内容 |
| --- | --- | --- |
| 匹配策略、随机控制和 FEVER 延迟 | `analyses/rq2_policy_comparison/` | 根据发布动作和路线结果重新评分 |
| 效用来源分层和切换分析 | `analyses/rq3_utility_sources/` | 校验发布摘要及其算术关系 |
| 成本偏好、路线复现和学习器检查 | `analyses/rq4_robustness/` | 校验发布摘要及其闭合关系 |
| 证据深度、结构化控制和可预测性 | `analyses/rq5_route_value/` | 校验发布摘要及其闭合关系 |
| 发布的评价方任务包 | `replays/` | 在不重跑检索的情况下校验台账和评分 |
| 从原始语料重跑检索与模型推理 | `full_replay/` | 提供高资源流程说明，不随仓库附带数据和模型下载 |

“数值闭合”表示校验论文使用的发布数值及其关系，但不重新生成出版图片。这样可以
避免把源表校验误解成完整重绘。

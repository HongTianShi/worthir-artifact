# 论文结果映射

本映射仅对应：

- **论文：** *WorthIR: An Evaluation Protocol for Cost-Aware Retrieval Routing*
- **版本：** 2026-08-16 submission
- **Artifact：** [v1.2.1](https://github.com/HongTianShi/worthir-artifact/releases/tag/v1.2.1)

`PAPER_SPEC.json` 是机器可读的唯一清单。`python run.py` 会检查下列每一项均已生成，并写出可点击的 `reproduced/INDEX.md`。

## 正文

| 论文项目 | 主要发布输入 | 输出 | 复现层级 |
| --- | --- | --- | --- |
| Figure 1 | `paper_reproduction/assets/figure1.png` | `reproduced/paper/figure1.pdf` | 冻结稿件图片导出 |
| Figure 2 | TREC-DL 与结构化任务 ledger、FEVER 冻结动作、FiQA 诊断结果 | `reproduced/paper/figure2.pdf` | 完整重绘 |
| Figure 3 | `paper_reproduction/inputs/figure3_decomposition.csv` | `reproduced/paper/figure3.pdf` | 完整重绘与算术闭合 |
| Figure 4 | `analyses/rq3_utility_sources/data/query_strata.csv` | `reproduced/paper/figure4.pdf` | 完整重绘 |
| Figure 5 | `analyses/rq4_robustness/data/cost_preference_curves.csv` | `reproduced/paper/figure5.pdf` | 完整重绘 |
| Figure 6 | `analyses/rq5_route_value/data/rq5_fever_gold_rank_band_routes.csv` | `reproduced/paper/figure6.pdf` | 完整重绘 |
| Figure 7 | FEVER 延迟与匹配策略结果 | `reproduced/paper/figure7.pdf` | 完整重绘 |
| Table 1 | 已注册的任务与路线说明 | `reproduced/paper/table1.csv` | 冻结任务定义导出 |
| Table 2 | TREC-DL query--route ledgers 与 FiQA 诊断结果 | `reproduced/paper/table2.csv` | 逐查询重算与诊断闭合 |
| Table 3 | 跨任务策略摘要与 Holm 检验 | `reproduced/paper/table3.csv` | 发布动作聚合与检验闭合 |
| Table 4 | FEVER 匹配路线集合结果 | `reproduced/paper/table4.csv` | 冻结动作摘要与稿件区间核对 |
| Table 5 | `paper_reproduction/inputs/table3_recoverability.csv` | `reproduced/paper/table5.csv` | 算术闭合 |
| Table 6 | held-out 路线价值摘要 | `reproduced/paper/table6.csv` | 摘要闭合 |

表号均以 2026-08-16 稿件为准，内部 RQ 文件名不代表论文表号。

## 附录

附录输出直接使用论文标签：

- Tables A.1--A.2：`appendix_table_a1.csv`、`appendix_table_a2.csv`
- Tables B.1--B.2：`appendix_table_b1.csv`、`appendix_table_b2.csv`
- Table C.1：`appendix_table_c1.csv`
- Tables D.1--D.2：`appendix_table_d1.csv`、`appendix_table_d2.csv`
- Tables E.1--E.6：`appendix_table_e1.csv` 至 `appendix_table_e6.csv`
- Figures E.1--E.2：`appendix_figure_e1.pdf`、`appendix_figure_e2.pdf`
- Figures F.1--F.2：`appendix_figure_f1.pdf`、`appendix_figure_f2.pdf`

生成的 `reproduced/INDEX.md` 会记录每一项的 caption、输出、状态和复现层级。

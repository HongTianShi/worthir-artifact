# 2026-08-16 论文结果

**论文：** *WorthIR: An Evaluation Protocol for Cost-Aware Retrieval Routing*

**论文版本：** 2026-08-16 submission

**发布 artifact：** [v1.3.1](https://github.com/HongTianShi/worthir-artifact/releases/tag/v1.3.1)

运行：

```bash
python run.py
```

该命令从发布的 query--route ledgers、冻结路线选择和冻结诊断摘要复算论文结果；它不会下载原始语料、重建索引、训练模型或重新运行路线推理。本地环境使用 `requirements-lock.txt` 安装，其中固定并验证了全部直接与传递依赖；`requirements.txt` 保留为简短的人工可读依赖表。

输出会持续保存在：

- `reproduced/INDEX.md`：全部论文图表的可点击总索引；
- `reproduced/paper/figure1.pdf` 至 `figure7.pdf`；
- `reproduced/paper/table1.csv` 至 `table6.csv`；
- 按论文标签命名的附录文件，例如 `appendix_figure_e1.pdf`；
- `reproduced/rqs/`：RQ2--RQ5 辅助结果；
- `reproduced/validation.json`：执行命令、耗时与最终状态。

## 正文结果

| 项目 | 内容 | 输出 | 复现层级 |
| --- | --- | --- | --- |
| Figure 1 | WorthIR 评估协议 | `figure1.pdf` | 冻结稿件图片导出 |
| Figure 2 | 效果--成本曲线 | `figure2.pdf` | 完整重绘 |
| Figure 3 | FEVER 效用分解 | `figure3.pdf` | 完整重绘与算术闭合 |
| Figure 4 | 路由机会贡献 | `figure4.pdf` | 完整重绘 |
| Figure 5 | 成本偏好敏感性 | `figure5.pdf` | 完整重绘 |
| Figure 6 | FEVER 重排序价值来源 | `figure6.pdf` | 完整重绘 |
| Figure 7 | FEVER 在线延迟审计 | `figure7.pdf` | 完整重绘 |
| Table 1 | 任务、路线与指标 | `table1.csv` | 冻结任务定义导出 |
| Table 2 | 成本下的固定策略偏好 | `table2.csv` | 逐查询重算与诊断闭合 |
| Table 3 | 跨任务路由比较 | `table3.csv` | 发布动作聚合与 Holm 检验闭合 |
| Table 4 | FEVER 匹配路线集合 | `table4.csv` | 冻结动作摘要 |
| Table 5 | 可恢复机会 | `table5.csv` | 算术闭合 |
| Table 6 | 路线特定效用关联 | `table6.csv` | held-out 摘要闭合 |

精确 caption、附录项目和文件要求见 [`PAPER_SPEC.json`](PAPER_SPEC.json)，人工可读的输入输出关系见 [`PAPER_MAP.md`](PAPER_MAP.md)。

`analyses/` 保存 RQ2--RQ5 结果，`replays/` 保存任务 ledger 与评分器，`paper_reproduction/` 保存稿件输入和绘图程序，`full_replay/` 提供原始路线重建入口。仓库不包含大型语料、索引、模型权重和原始排名。

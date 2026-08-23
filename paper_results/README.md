# 论文结果

该目录包含复现 WorthIR 论文结果所使用的数据和代码。

从该目录运行：

```bash
python run.py
```

该命令会创建本地环境，复现论文图表，重新生成 RQ2--RQ5 摘要，并验证已发布的
任务 ledger。所有输出都会保留：

- `reproduced/paper/`：重建的论文图、表和报告；
- `reproduced/rqs/`：重建的 RQ2--RQ5 摘要；
- `reproduced/validation.json`：校验步骤和最终状态。

论文项目、仓库输入、命令和输出之间的对应关系见
[`PAPER_MAP.md`](PAPER_MAP.md)。

主要内容如下：

- `analyses/`：RQ2--RQ5 结果表和动作文件。
- `replays/`：已发布的任务 ledger 和特定任务评分器。
- `paper_reproduction/`：图表输入与生成程序。
- `full_replay/`：重建检索输出所需的条件。
- `docs/`：参照语义、数据来源和第三方条款。

仓库不包含大型语料库、索引、模型权重或原始排名结果。

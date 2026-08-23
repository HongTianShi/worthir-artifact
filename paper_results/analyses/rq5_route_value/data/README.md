# RQ5 路线价值诊断

这些 CSV 文件用于分析哪些推理时信号与特定路线的效用增益相关。内容包括路线价值
预测、难度内关联、难度分组异质性、信息块对照、操作对照、FEVER 相关页面排名分组、
问题类型特征及互补性摘要。

若干字段只用于评测端诊断，不能描述为路由器输入。分析是关联性的而非因果性的；
应采用结果表中规定的术语和取整方式。

`python paper_results/run.py` 会校验这些发布摘要，并将主要可预测性和操作对照表
复制到 `paper_results/reproduced/rqs/`。Figure 6 和 Table 6 的对应关系见
`paper_results/PAPER_MAP.md`。

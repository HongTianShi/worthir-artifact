# 论文结果复现

该软件包根据精简的已发布输入重建图 1--3 和表 2--4，不执行路线推理、拟合或模型选择。

```bash
python scripts/reproduce_paper.py --output-dir reproduced/paper
```

- 图 1 使用一个 TREC-DL 2019 协议示例。
- 图 2 验证 FiQA-Compression260 路线坐标。
- 图 3 绘制各任务从固定路线到 Oracle 的恢复比例。
- 表 2 根据完整的 TREC-DL 路线 ledger 重新计算。
- 表 3 验证增益和已恢复空间之间的恒等关系。
- 表 4 根据匹配预算的逐查询审计重新汇总。

验证会检查绘图坐标、表格计算、行数和生成文件是否存在。

# `worthir_eval` 软件包

该软件包实现精简的 WorthIR 评测接口。

- `core.py` 加载契约和动作向量，验证路线依赖关系和累计成本，接入仅评测端可见的
  结果，并计算有效性、成本、效用和遗憾摘要。
- `analysis.py` 计算明确隔离的组织者逐查询诊断、lambda 敏感性、硬预算汇总和
  固定路线 Pareto 点。
- `__init__.py` 导出受支持的公共符号。

`inspect_task()` 在评分前校验并汇总任务，`load_and_score()` 评估一个与契约绑定的
动作文件。
`per_query_analysis()`、`sensitivity_analysis()`、`budget_analysis()` 和
`fixed_route_points()` 需要 evaluator 数据，不能生成路由器输入。

该软件包保持参与者与评测者之间的信息边界：参与者可见输入足以生成动作，完整的
路线结果只在评测时接入。

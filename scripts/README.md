# CLI 命令索引

通过 PyPI 安装的用户通常直接运行 `worthir`；源码用户使用 `worthir.cmd` 或
`./worthir`。下列文件实现这些公开命令。

- `build_trec_task.py`：将 qrels、TREC run 和成本转换为任务。
- `build_custom_task.py`：根据通用查询、路线、结果和成本表构建任务。
- `validate_task.py`：在评分前校验完整任务。
- `actions_from_csv.py`：将“查询--路线”选择 CSV 绑定到任务。
- `compare_policies.py`：评估策略和固定路线并写出报告。
- `score_actions.py`：评估一个动作文件。
- `analyze_task.py`：写出组织者专用逐查询诊断。
- `sensitivity.py`：在 lambda 网格上评价冻结动作。
- `budget.py`：汇总逐查询硬成本上限。
- `plot_pareto.py`：绘制无额外依赖的描述性 Pareto SVG。
- `init_task.py`：复制可编辑任务模板。
- `run_smoke_test.py`、`run_integrity_tests.py` 和 `validate_framework.py`：
  `worthir doctor` 使用的框架检查。

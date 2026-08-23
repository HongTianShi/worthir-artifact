# 内部命令

大多数用户应通过 `worthir.cmd` 或 `./worthir` 调用 `worthir.py`。

- `build_trec_task.py`：将 qrels、TREC run 和成本转换为任务。
- `actions_from_csv.py`：将“查询--路线”选择 CSV 绑定到任务。
- `compare_policies.py`：评估策略和固定路线并写出报告。
- `score_actions.py`：评估一个动作文件。
- `init_task.py`：复制可编辑任务模板。
- `run_smoke_test.py`、`run_integrity_tests.py` 和 `validate_framework.py`：
  `worthir doctor` 使用的框架检查。

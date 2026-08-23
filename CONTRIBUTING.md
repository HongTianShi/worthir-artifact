# 参与贡献

欢迎提交错误修复、更清楚的任务适配器和新的可运行示例。

提交 pull request 前请运行：

```bash
python scripts/validate_framework.py
python paper_results/run.py
```

接入新任务时，请在 `examples/` 中提供一个采用合成数据或可再分发数据的小型示例，说明效果指标、成本来源和 Router 可见的信息。Evaluator outcomes 不得进入 participant inputs。请对生成任务运行 `worthir validate-task`，并在 README 中给出准确命令。

请勿提交下载的语料、模型权重、索引、本地虚拟环境或生成的任务输出。每个 pull request 只保留读者运行或理解该改动所需的内容。

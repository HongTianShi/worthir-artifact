# 可运行示例

选择最接近自身任务的入口：

- [`custom_task/`](custom_task/)：从通用 CSV 构建并校验任务，不要求 TREC 格式。
- [`custom_router/`](custom_router/)：只读取参与者可见信息，生成冻结路线选择，
  并与固定路线比较。
- [`python_api/`](python_api/)：不经过 CLI，直接从 Python 调用 WorthIR。
- [`trec_walkthrough/`](trec_walkthrough/)：将 qrels 和 TREC runs 转换成 WorthIR 任务。

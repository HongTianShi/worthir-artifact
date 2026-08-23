# Python API

构建任意 WorthIR 任务后，可以不经过 CLI，直接检查并评分：

```bash
python examples/python_api/example.py reproduced/custom_task
```

`inspect_task` 检查任务契约、公开信息、路线依赖和完整 evaluator ledger；`load_and_score` 再把已绑定契约的动作文件与隐藏 ledger 合并，返回效果、成本、效用、遗憾和路线计数。

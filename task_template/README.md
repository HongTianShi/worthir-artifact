# 可编辑任务模板

`worthir init` 会复制这个可运行的单查询任务。替换示例路线、参与者可见状态、
动作和完整评测 ledger，然后从仓库根目录运行 `worthir compare TASK_DIR`。

该模板使用决策时已知的固定成本，因此同一累计成本同时写在
`contracts/route_registry.json` 的路线记录和评价方 ledger 中。两处不一致时，
`validate-task` 会拒绝任务。

契约还声明了示例 lambda 与硬预算网格。动作冻结后，`worthir analyze`、
`worthir sensitivity`、`worthir budget` 和 `worthir plot` 会把 evaluator 专用
诊断写入 `organizer_private/`。

大多数任务使用 `worthir build-custom` 比手动编辑该模板更快，也更不容易出错。
标准 qrels 和 TREC run 可使用 `worthir build-trec`。

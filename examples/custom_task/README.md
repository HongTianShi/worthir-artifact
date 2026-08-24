# 自定义任务输入

这个示例不是 TREC 排序任务。它使用 `answer_coverage` 作为有效性指标，并且执行
成本随查询变化。

四个源文件构成完整的通用适配器接口：

- `task.json`：声明有效性指标、成本配置以及可选的 lambda 和硬预算网格；
- `queries.csv`：仅包含路由器可使用的信息；
- `routes.csv`：定义可用路线、前置关系和路线成本；
- `outcomes.csv`：包含评价方可见的完整查询--路线有效性与成本结果。

在仓库根目录构建并校验：

```powershell
.\worthir.cmd build-custom examples/custom_task/source reproduced/custom_task
.\worthir.cmd validate-task reproduced/custom_task
```

```bash
./worthir build-custom examples/custom_task/source reproduced/custom_task
./worthir validate-task reproduced/custom_task
```

已有累计成本时使用 `cost`；需要工具对传递前置闭包求和时使用
`incremental_cost`。在 `outcomes.csv` 中加入同名列即可提供逐查询成本。
将 `cost_profile.availability` 设为 `known_at_commitment`，表示路由器可在选择路线前
使用成本；构建器会把固定成本写入路线注册表，或把逐查询成本写入
`participant/route_costs.csv`。若成本只能在执行后测量，则使用
`measured_after_execution`。

评价结束后，任务组织者可以运行 `worthir analyze`、`worthir sensitivity`、
`worthir budget` 和 `worthir plot`。这些命令写入 `organizer_private/`；其中的
逐查询和 oracle 字段不能作为路由器输入。

# 自定义任务输入

这个示例不是 TREC 排序任务。它使用 `answer_coverage` 作为有效性指标，并且执行
成本随查询变化。

四个源文件构成完整的通用适配器接口：

- `task.json`：声明有效性指标和成本配置；
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

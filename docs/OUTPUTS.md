# 阅读 WorthIR 输出

## 策略比较

`comparison.csv` 和 `comparison.md` 报告：

- **平均有效性：** 所选路线对应的任务指标；
- **平均成本：** 所选路线的累计成本；
- **平均效用：** 有效性减去 lambda 与成本的乘积；
- **相对固定路线的 Delta U：** 与开发集选定固定路线之间的效用差；
- **平均遗憾：** 与每个查询在已注册路线中最佳路线之间的差；
- **Oracle 匹配比例：** 策略选择评测端最佳路线的查询比例。

开发集选定的固定路线是可部署参照。逐查询 Oracle 不可部署，只用于衡量已注册
路线集合内存在多少机会。

## 固定路线与 Pareto 曲线

`fixed_routes.csv` 报告每条固定路线。`pareto=true` 表示不存在另一条固定路线，
在平均有效性不低且平均成本不高的同时，至少有一项严格更优。

自适应策略是按查询加权的路线组合，不必与任何固定路线点重合。

## 通用报告的解释范围

通用比较只提供描述性结果。它不会推断置信区间、选择 lambda 或声称结果能够跨任务
迁移。只有当重采样单位符合任务的依赖结构，而且策略在接入评测结果前已经冻结时，
才应加入重采样分析。

## 组织者专用逐查询结果

`worthir analyze TASK` 写入 `organizer_private/per_query_scores.csv`。每行包含
已选路线的有效性、成本和效用，开发集固定参照，路线集合内的 oracle，遗憾和三类
机会分层之一。该文件包含查询标识符与 evaluator 结果，不能提供给路由器，也不能
复制到 `participant/`。

面向参与者的聚合命令 `worthir score` 仍然不返回查询标识符。

## Lambda 敏感性与硬成本上限

`worthir sensitivity TASK` 对每个 lambda 报告策略、固定参照和 oracle 的效用。
策略动作保持冻结，只有 evaluator 侧的效用计算发生变化。

`worthir budget TASK` 将每个声明值视为逐查询累计成本硬上限，报告可行路线中的
evaluator 专用有效性包络、冻结策略的可行比例和开发集固定路线的可行比例。命令
不会暗中替换超出预算的策略动作。

两张表都包含 `prespecified`、`scope` 和 `interpretation`。从任务契约读取的网格
属于预先声明；不同的命令行网格不属于预先声明。

## Pareto SVG

`worthir plot TASK` 无需额外绘图库，直接写入
`organizer_private/pareto.svg`。蓝点表示固定路线，蓝线连接非支配固定路线点，
橙色菱形表示冻结策略均值。该图是描述性的 evaluator 专用结果。

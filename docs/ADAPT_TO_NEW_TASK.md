# 将 WorthIR 用于一个检索任务

最短路径从标准 qrels 和 TREC run 文件开始。以下命令均应从仓库根目录运行。

## 1. 创建源文件夹

```text
my_source/
  qrels.tsv
  routes.csv
  queries.csv              可选
  costs.csv                可选
  policy_choices.csv       可选
  runs/
    base.trec
    advanced.trec
```

`qrels.tsv` 接受常见的四列 TREC 格式：

```text
query_id 0 document_id relevance
```

也接受三列的 `query_id document_id relevance` 记录。

每个 run 文件均采用六列 TREC run 格式：

```text
query_id Q0 document_id rank score run_name
```

`routes.csv` 必须包含以下各列：

```csv
route_id,label,parent_route_id,run_file,cost,development_selected
base,BM25,,runs/base.trec,0.00,false
advanced,Cross-encoder,base,runs/advanced.trec,0.75,true
```

必须且只能将一条路线标记为 `development_selected`。它是在不使用评测结果的
前提下选出的强固定参照。`parent_route_id` 记录执行该路线前必须完成的工作。
成本是累计成本，因此子路线的成本不得低于其父路线。

如果一条路线对所有查询的成本都相同，使用 `cost` 列即可。如果延迟或工作量随
查询变化，则添加 `costs.csv`，并为每个“查询--路线”组合提供一行：

```csv
query_uid,route_id,cost
q1,base,12.4
q1,advanced,48.7
```

提供 `costs.csv` 后，其中的数值将取代固定路线成本。选择成本尺度和 lambda 前，
请阅读 [`COST_AND_LAMBDA.md`](COST_AND_LAMBDA.md)。

`queries.csv` 是参与者可见的状态。第一列必须是 `query_uid`，并且 qrels 中的
每个查询都必须恰好出现一次。该文件只能包含路线选择前已经可用的信息。如果省略，
WorthIR 会写出只含查询编号的一列。

`policy_choices.csv` 为可选文件，包含两列：

```csv
query_uid,selected_route_id
q1,base
q2,advanced
```

如果省略该文件，生成的默认策略会对每个查询选择开发集选定的固定路线。如果提供
该文件，请在构建任务时使用 `--policy-id` 为策略指定一个有意义的名称。

## 2. 构建并检查任务

```powershell
.\worthir.cmd build-trec my_source my_task --task-id my-retrieval-task-v1 --metric ndcg@10 --lambda 0.08 --policy-id my-router
```

在 macOS 或 Linux 上使用 `./worthir`。构建后的任务包含：

```text
my_task/
  contracts/task_contract.json
  contracts/route_registry.json
  participant/legal_state.csv
  participant/actions.json
  participant/policies/
  evaluator/ledger.csv
```

适配器会为 qrels 中的每个查询和每个已注册 run 计算 NDCG@K。继续前请抽查
若干 ledger 记录。相关性标注和 ledger 属于评测端数据，路由策略不得使用它们。

## 3. 添加路由策略

将每个策略在留出数据上的选择导出为包含 `query_uid` 和
`selected_route_id` 的 CSV，然后将其绑定到任务：

```powershell
.\worthir.cmd actions my_task choices.csv --policy-id my-router
```

生成的 JSON 位于 `my_task/participant/policies/my-router.json`。如果缺少查询、
查询重复或选择了未知路线，命令会拒绝该输入。

## 4. 比较策略

```powershell
.\worthir.cmd compare my_task
```

该命令会评估默认动作文件、`participant/policies/` 中的每个 JSON 文件以及每条
已注册的固定路线，并写出：

- `comparison.md`：便于阅读的任务摘要；
- `comparison.csv`：各策略和固定路线的均值；
- `fixed_routes.csv`：固定路线点及其是否属于 Pareto 曲线；
- `comparison.json`：完整的机器可读输出。

结果解释见 [`OUTPUTS.md`](OUTPUTS.md)。这些文件报告描述性查询均值。统计区间
需要使用与任务相匹配的重采样设计，通用工具不会凭空生成统计区间。

## 手动构建

对于不采用 TREC 有效性指标的任务，可以创建一个可编辑任务，再将示例 ledger
替换为完整的“查询--路线”矩阵：

```powershell
.\worthir.cmd init my_task --task-id my-task-v1
.\worthir.cmd score my_task
```

ledger 的列为 `query_uid,route_id,effectiveness,cost`。有效性指标必须是越高越好，
并且位于任务契约声明的范围内。

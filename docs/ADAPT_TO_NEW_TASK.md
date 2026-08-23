# 将 WorthIR 用于新任务

以下命令均在仓库根目录运行。除非数据已经是 qrels 和 TREC run，否则优先使用
通用适配器。

## 通用任务

创建一个源目录：

```text
my_source/
  task.json
  queries.csv
  routes.csv
  outcomes.csv
  policy_choices.csv       可选
```

### 1. 声明指标和成本配置

`task.json` 声明一个“越高越好”的有效性指标，以及效用公式
`utility = effectiveness - lambda * cost` 中的成本偏好：

```json
{
  "task_id": "my-task-v1",
  "metric": {
    "name": "answer_coverage",
    "minimum": 0.0,
    "maximum": 1.0,
    "higher_is_better": true
  },
  "cost_profile": {
    "profile_id": "latency-seconds-v1",
    "provenance": "由独立校准集估计、在路线选择前可获得的预计执行时间",
    "lambda": 0.15,
    "availability": "known_at_commitment"
  },
  "development_selected_fixed_route": "standard"
}
```

指标不必是 NDCG 或其他 TREC 指标。WorthIR 直接使用每个查询--路线组合对应的
数值结果。

### 2. 分离路由器输入与评价方结果

`queries.csv` 只能包含路由决策发生时已经可用的字段，第一列必须是
`query_uid`：

```csv
query_uid,question_length,domain
q1,12,sports
q2,31,science
```

`outcomes.csv` 只供评价方使用，并且必须包含每个查询--路线组合：

```csv
query_uid,route_id,effectiveness
q1,standard,0.81
q1,extended,0.89
q2,standard,0.64
q2,extended,0.91
```

除非任务的数据划分明确将这些行定义为开发数据，否则不得用此文件训练或执行
留出集上的路由器。

### 3. 定义路线和成本

多个前置路线以分号分隔。必须且只能有一条在开发数据上选出的固定参考路线。

如果已经有累计成本：

```csv
route_id,label,prerequisites,cost,development_selected
standard,标准路线,,0.10,true
extended,扩展路线,standard,0.40,false
```

如果路线由依赖图中的多个组件组成，则使用 `incremental_cost`：

```csv
route_id,label,prerequisites,incremental_cost,development_selected
lexical,词法检索,,0.03,false
semantic,语义检索,,0.12,true
combined,联合复核,lexical;semantic,0.08,false
```

WorthIR 会对传递前置闭包求和，并且每个组件只计一次。若成本随查询变化，可在
`outcomes.csv` 中加入同名的 `cost` 或 `incremental_cost` 列，并为每个组合
提供数值。两种成本模式不能混用。

当 `availability` 为 `known_at_commitment` 时，构建器会把固定成本写入
`contracts/route_registry.json`，或把逐查询累计成本写入
`participant/route_costs.csv`。若路由器在路线执行前无法知道成本，则使用
`measured_after_execution`；这类成本只留在评价方。

### 4. 构建并校验

```powershell
.\worthir.cmd build-custom my_source my_task
.\worthir.cmd validate-task my_task
```

```bash
./worthir build-custom my_source my_task
./worthir validate-task my_task
```

校验结果会汇总查询数、路线数、缺失组合、依赖问题、累计成本问题、成本何时可见，
并检查每个公开成本是否与评价方 ledger 一致。

### 5. 运行并比较路由器

路由器读取任务契约、公开路线注册表、`my_task/participant/legal_state.csv` 和所有
公开成本，并输出：

```csv
query_uid,selected_route_id
q1,standard
q2,extended
```

一条命令完成绑定和比较：

```powershell
.\worthir.cmd evaluate my_task choices.csv --policy-id my-router
```

[`examples/custom_router/`](../examples/custom_router/) 给出了一个从不读取
评价方台账的完整示例。

## TREC 适配器

如果使用 qrels 和六列 TREC run，请参照
[`examples/trec_walkthrough/`](../examples/trec_walkthrough/)。其
`routes.csv` 额外包含 `run_file` 列，`build-trec` 会先计算 NDCG@K，再生成
同样的任务结构：

```powershell
.\worthir.cmd build-trec my_source my_task --task-id my-task-v1 --metric ndcg@10 --lambda 0.08
.\worthir.cmd validate-task my_task
```

可选的 TREC `costs.csv` 使用 `query_uid,route_id,cost` 三列提供逐查询累计成本。
只有当这些成本在路线选择时尚不可知，才添加
`--cost-availability measured_after_execution`。

## 输出

`compare` 和 `evaluate` 会生成可读的 `comparison.md`、机器可读的 CSV 和
JSON，以及带 Pareto 成员标记的 `fixed_routes.csv`。这些结果是描述性查询均值。
统计区间需要与任务相适应的重采样设计，通用工具不会自行生成。

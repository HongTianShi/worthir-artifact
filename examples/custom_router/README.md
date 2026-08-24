# 使用自己的路由器

在仓库根目录运行完整示例：

```powershell
.\worthir.cmd demo-custom
```

```bash
./worthir demo-custom
```

该示例会构建非 TREC 任务，运行 `router.py`，将 CSV 决策绑定到任务契约，并与
所有固定路线比较。报告位于 `reproduced/custom_task/comparison.md`。

`router.py` 读取公开任务契约、路线注册表、lambda、
`participant/legal_state.csv` 和 `participant/route_costs.csv`。它按“预测有效性减去
lambda 乘公开成本”选择路线，从不读取包含决策时不可用信息的
`evaluator/ledger.csv`。使用自己的路由器时，只需替换
`predicted_effectiveness()` 并保留两列输出格式：

```text
query_uid,selected_route_id
```

对于已有任务，可用一条命令评价该 CSV：

```powershell
.\worthir.cmd evaluate TASK choices.csv --policy-id my-router
```

```bash
./worthir evaluate TASK choices.csv --policy-id my-router
```

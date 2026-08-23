# TREC 完整示例

这是一个采用标准 TREC 格式的小型检索任务，无需下载数据即可演示完整的人类操作流程。

```powershell
.\worthir.cmd demo
```

```bash
./worthir demo
```

该命令根据 `source/qrels.tsv` 和三个 TREC run 计算 NDCG@3，构建 WorthIR
任务，评估提供的策略和每条固定路线，并写出
`reproduced/trec_walkthrough/comparison.md`。

运行示例后，可按以下方式尝试另一个策略：

```powershell
.\worthir.cmd actions reproduced/trec_walkthrough examples/trec_walkthrough/source/alternative_choices.csv --policy-id alternative
.\worthir.cmd compare reproduced/trec_walkthrough
```

```bash
./worthir actions reproduced/trec_walkthrough examples/trec_walkthrough/source/alternative_choices.csv --policy-id alternative
./worthir compare reproduced/trec_walkthrough
```

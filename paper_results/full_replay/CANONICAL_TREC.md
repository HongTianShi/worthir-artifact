# TREC-DL 原始重建

`replays/canonical_trec/` 下的精简软件包足以进行动作评分和汇总结果复现。重建原始
路线还需要 MS MARCO passage 语料库、TREC-DL 2019/2020 topic 和 qrels、指定的
Pyserini 索引及已注册重排检查点。

必须保持 `public/contracts/route_registry.json` 和 `cost_contract.json` 中定义的
路线顺序及累计父路线成本。

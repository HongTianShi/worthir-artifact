# 完整回放指南

该目录说明已发布的精简 ledger 与原始检索重建之间的关系。这里有意只提供指南，
而不包含大型语料库、索引、模型检查点或受许可限制的数据。

- `RESOURCE_REQUIREMENTS.md` 说明硬件、存储、时间和依赖要求，应首先阅读。
- `CANONICAL_TREC.md`、`FEVER.md` 和 `MUSIQUE.md` 说明特定任务的重建输入
  和路线执行方式。
- `STRUCTURED_AND_DIAGNOSTIC.md` 说明 Structured-v2 和其余诊断任务。

常规 artifact 使用流程不需要完整回放。只有在重建原始路线结果时才使用这些文档，
不要将精简 ledger 的复现描述成与语料库和索引重建等价。

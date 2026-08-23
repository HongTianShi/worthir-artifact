# 第三方数据与模型声明

仓库根目录的 MIT 许可证仅覆盖 WorthIR 自有代码和文档，不会对第三方数据集、
相关性标注、查询、模型检查点或由其衍生的记录重新授权。

| 资源 | 包含的字段或记录 | 来源与适用条款 | 转换 |
| --- | --- | --- | --- |
| MS MARCO / TREC Deep Learning 2019--2020 | 97 个 topic 的官方 ID、查询文本、BM25 文档 ID 和分数、查询统计、冻结动作及逐路线指标 | [MS MARCO 数据集与条款](https://microsoft.github.io/msmarco/Datasets.html)；[TREC DL 数据](https://trec.nist.gov/data/deep.html)。MS MARCO 将该数据集限于非商业研究。 | 增加查询统计、排名标识、路线成本和有效性/效用记录；不包含 passage 文本、原始 qrels 和完整排名。 |
| FEVER | 13,332 条 claim 的官方开发集 claim、归一化 claim、标签、证据集计数、路线选择时特征、动作及逐路线证据页面指标 | [FEVER 数据集](https://fever.ai/dataset/fever.html) 和 [FEVER 数据许可证声明](https://fever.ai/download/fever/license.html)。标注包含 Wikipedia 材料，仍受适用的 Wikipedia 条款或 CC BY-SA 3.0 约束。 | 对 claim 进行归一化，并增加检索特征、路线成本、动作和文档检索结果；不包含 Wikipedia 语料库、索引和检查点。 |
| 2WikiMultiHopQA | 问题、评测记录中的支持标题标识符、路线选择时特征、分组动作及逐路线支持标题指标 | [2WikiMultiHopQA 仓库](https://github.com/Alab-NII/2wikimultihop)，Copyright 2020 Xanh Ho，Apache License 2.0；许可证副本位于 `third_party/2WikiMultiHopQA-LICENSE.txt`。 | 为问题分配任务 ID 和折叠，并增加图/上下文特征、成本、动作和检索结果；不包含源语料实例化结果和超链接语料库。 |
| MuSiQue | 问题、分解问题、段落标题、评测记录中的支持标题/答案字段、路线选择时特征、动作及逐路线指标 | [MuSiQue 仓库](https://github.com/stonybrooknlp/musique)，Trivedi 等人；发布数据采用 CC BY 4.0。 | 为官方记录分配任务 ID，并增加路线特征、成本、动作和检索结果；不包含段落文本和已拟合模型。 |
| BEIR / FiQA | 查询/文档标识符、诊断路线指标、成本和完整性标识 | [BEIR 仓库与数据说明](https://github.com/beir-cellar/beir)；上游 FiQA 条款继续适用。 | 生成精简的成本--有效性诊断 ledger；不包含上游语料库和检查点。 |

所含数据记录用于非商业科学评测与回放。再次使用或分发时，用户必须遵守各上游许可证
或访问条件；根目录 MIT 许可证不授予任何额外数据权利。

重建文档使用公共检查点标识符引用具名神经模型。仓库不分发模型权重；模型卡和上游
许可证仍然适用。

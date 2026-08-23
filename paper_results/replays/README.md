# 任务回放

每个任务都实现同一份一次性动作契约，同时保留自己的有效性指标、路线集合、成本定义
和证据属性。

| 任务 | 入口 | 证据类型 |
| --- | --- | --- |
| TREC-DL | `canonical_trec/README.md` | 回顾性任务 |
| FEVER | `fever/README.md` | 回顾性任务 |
| 2Wiki-Structured | `structured_v2/README.md` | 分组 OOF 任务 |
| Hyperlink10k | `hyperlink10k/README.md` | 依赖性压力测试 |
| MuSiQue | `musique/README.md` | 官方数据划分任务 |
| FiQA260 | `fiqa260/README.md` | 公开标签诊断 |
| Dense-standard | `dense_and_legacy_recoverability/README.md` | 诊断回放 |

部分目录仍保留 `organizer_private` 路径名，表示选择动作时其中内容只对评测者可见。
即使 ledger 已经发布，也绝不能将其用作策略输入。

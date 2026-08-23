# 原始路线重建资源

下表是规划范围，不是性能结论。耗时取决于硬件、batch、索引是否已有和缓存状态；磁盘估计包含索引工作副本及中间路线输出。

| 任务 | 外部材料 | 磁盘 | RAM | VRAM | 20 查询 smoke | 完整运行 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| TREC-DL | MS MARCO、topics/qrels、索引、模型 | 80--140 GB | 32 GB | 建议 12 GB | 20--60 分钟 | 12--48 GPU 小时 |
| FEVER | 2017 Wikipedia、Lucene 索引、模型、候选缓存 | 120--220 GB | 32 GB | 建议 12 GB | 20--60 分钟 | 10--30 GPU 小时 |
| 2Wiki/Hyperlink10k | 数据快照、证据文本、模型 | 10--30 GB | 16 GB | 建议 8 GB | 10--30 分钟 | 1--6 GPU 小时 |
| MuSiQue | 数据快照、段落证据、模型 | 10--20 GB | 16 GB | 建议 8 GB | 10--30 分钟 | 1--4 GPU 小时 |
| FiQA260 | 查询快照、dense 索引、模型 | 50--120 GB | 32 GB | 建议 12 GB | 15--45 分钟 | 3--12 GPU 小时 |
| Dense-standard | 五个数据快照、dense 索引、encoder | 50--150 GB | 32 GB | 建议 12 GB | 15--45 分钟 | 4--18 GPU 小时 |

常规 `python paper_results/run.py` 不需要上述外部材料。上游数据和模型许可证仍然有效。

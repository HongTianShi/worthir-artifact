# 重建原始检索路线

该流程位于发布 ledger 的上游：检查用户另行取得的语料与模型，调用任务适配器，把完整 query--route outcomes 转为 WorthIR ledger，并验证结果。仓库不再分发这些外部材料。FiQA-Compression260 不需要手工准备索引；任务适配器会下载公开语料和模型，并在本地构建所需表示。

运行 FiQA 重建：

```bash
python -m pip install -r paper_results/full_replay/fiqa260/requirements.txt
python paper_results/full_replay/replay.py fiqa260 prepare --workspace replay-work/fiqa260
python paper_results/full_replay/replay.py fiqa260 smoke --workspace replay-work/fiqa260
```

完整 260 查询运行见 [`FIQA260.md`](FIQA260.md)。

先选择任务和一个空工作目录：

```bash
python paper_results/full_replay/replay.py fever prepare \
  --workspace replay-work/fever \
  --input wikipedia=/data/fever/wiki-pages \
  --input index=/data/fever/lucene-index \
  --input checkpoints=/models/fever \
  --input candidate_cache=/data/fever/bm25-candidates
```

`prepare` 会写出 `replay.json`，列出缺失材料，复制一个很小的路线适配器模板，并打印资源估计。请按任务说明把模板替换为已注册路线的运行程序，或修改 `replay.json` 中的两组命令去调用现有程序。适配器须在 `--output` 目录写出 `task.json`、`queries.csv`、`routes.csv` 和 `outcomes.csv`。

每个任务都采用同样的五个阶段：

```bash
python paper_results/full_replay/replay.py fever prepare --workspace replay-work/fever
python paper_results/full_replay/replay.py fever smoke --workspace replay-work/fever
python paper_results/full_replay/replay.py fever run-routes --workspace replay-work/fever
python paper_results/full_replay/replay.py fever build-ledger --workspace replay-work/fever
python paper_results/full_replay/replay.py fever verify --workspace replay-work/fever
```

- `prepare`：检查并记录外部路径；
- `smoke`：要求适配器运行 20 个查询，并验证小型 ledger；
- `run-routes`：执行完整适配器；
- `build-ledger`：调用通用任务构建器；
- `verify`：检查 WorthIR 契约和注册的查询/路线数量。

最后仍需用 `python paper_results/run.py` 对发布结果做数值闭合。重建路线可能因硬件或上游模型版本产生小幅差异，发布 ledger 的复算则必须精确闭合。

下载数据前先读 [`RESOURCE_REQUIREMENTS.md`](RESOURCE_REQUIREMENTS.md)，再查看相应任务说明：

- [`CANONICAL_TREC.md`](CANONICAL_TREC.md)
- [`FEVER.md`](FEVER.md)
- [`FIQA260.md`](FIQA260.md)
- [`MUSIQUE.md`](MUSIQUE.md)
- [`STRUCTURED_AND_DIAGNOSTIC.md`](STRUCTURED_AND_DIAGNOSTIC.md)

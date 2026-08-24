# 重建 FiQA-Compression260

该流程从官方 BEIR FiQA 语料重建论文使用的八条 FiQA 路线。它会自动下载语料和两个已注册的公开模型，为全部 57,638 篇文档编码，在固定的 260 个查询上执行路线，并写出 WorthIR ledger；无需手工准备索引。

八条路线分别为摘要检索、二值 dense 检索、IVF--PQ、96 维与 192 维截断、int8 dense 检索、完整 dense 检索，以及对完整 dense 前 50 个结果进行 cross-encoder 重排。各路线注册的算子成本会在策略选路前写入公共路线注册表。

## 配置环境

使用 Python 3.10--3.13 环境。CPU 机器应运行仓库内置安装程序：它会先从 PyTorch 官方 CPU wheel 索引安装 PyTorch，再安装其余固定依赖，避免默认 Linux wheel 携带的 CUDA 运行库。

```bash
python paper_results/full_replay/fiqa260/install_cpu.py
```

如果机器配有受支持的 CUDA 或 ROCm 加速器，请先按照 PyTorch 官方选择器安装对应版本，再运行 `python -m pip install -r paper_results/full_replay/fiqa260/requirements.txt`。

准备工作目录。该命令会自动登记仓库内置的适配器：

```bash
python paper_results/full_replay/replay.py fiqa260 prepare --workspace replay-work/fiqa260
```

## 运行

Smoke test 运行 20 个已注册查询。首次运行还会下载语料和模型，并创建可复用的文档表示与索引。在一台仅使用 CPU 的 Windows 工作站上，一次性初始化约需 10 分钟；首次完成 260 个查询的 cross-encoder 阶段约需 3 分钟。两类缓存均存在后，完整路线运行约需 22 秒。实际耗时会随硬件和模型缓存状态变化。

```bash
python paper_results/full_replay/replay.py fiqa260 smoke --workspace replay-work/fiqa260
```

随后复用缓存完成 260 个查询的运行，构建 evaluator ledger，并检查任务契约：

```bash
python paper_results/full_replay/replay.py fiqa260 run-routes --workspace replay-work/fiqa260
python paper_results/full_replay/replay.py fiqa260 build-ledger --workspace replay-work/fiqa260
python paper_results/full_replay/replay.py fiqa260 verify --workspace replay-work/fiqa260
```

主要输出包括：

- `replay-work/fiqa260/task/evaluator/ledger.csv`：全部 2,080 个 query--route 结果；
- `replay-work/fiqa260/task/participant/legal_state.csv`：router 可见的查询状态；
- `replay-work/fiqa260/task/contracts/route_registry.json`：路线、前置关系和公共成本；
- `replay-work/fiqa260/fiqa260_rebuild_summary.json`：各路线重建均值与论文数值的对照。

程序会在解压前用已注册的 SHA256 检查官方 FiQA 压缩包。模型文件使用已注册的 Hugging Face 版本。适配器把下载的语料、文档表示、摘要索引和 IVF--PQ 索引保留在工作目录中，后续阶段不会重复计算。

两条截断路线、int8 路线、完整 dense 路线和 cross-encoder 路线是确定性的，程序会将其均值与论文数值核对。摘要检索、二值检索和 IVF--PQ 会受到 FAISS 聚类、近似搜索或二值分数并列排序的影响，因此程序会如实并列报告重建均值与论文数值，而不会用冻结结果替换本次运行结果。

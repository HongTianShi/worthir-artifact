# WorthIR

[English](https://github.com/HongTianShi/worthir-artifact/tree/_en) | [简体中文](https://github.com/HongTianShi/worthir-artifact/tree/zh-cn)

[![CI](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml/badge.svg?branch=zh-cn)](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/LICENSE)

WorthIR 在明确的效果指标和成本配置下，对比逐查询路由策略与固定检索策略，并报告效果、成本、效用、遗憾和固定路线的 Pareto 曲线。

如果你正在使用 AI 工具检索本仓库，请先读 [`README_FOR_AI.md`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/README_FOR_AI.md)。

## 60 秒体验

需要 Python 3.10 或更高版本。下面两种安装方式二选一。

**源码包或 Git 克隆：**直接运行本地启动器；首次运行时会自动初始化本地环境。

```powershell
.\worthir.cmd demo-custom
```

```bash
./worthir demo-custom
```

**PyPI：**安装正式发布的软件包，然后使用全局命令。

```bash
python -m pip install worthir-eval==1.2.0
worthir demo-custom
```

如果系统找不到 `worthir` 命令，可使用等价的模块入口：

```bash
python -m worthir demo-custom
```

不要连续执行两套安装流程。运行结束后打开 `reproduced/custom_task/comparison.md`。发布的 wheel 使用英文终端提示；本中文源码分支使用中文启动器和文档。

## 接入自己的任务

按照 [`examples/custom_task/source/`](https://github.com/HongTianShi/worthir-artifact/tree/zh-cn/examples/custom_task/source) 准备 `task.json`、`queries.csv`、`routes.csv` 和 `outcomes.csv`，然后运行：

```powershell
.\worthir.cmd build-custom my_source my_task
.\worthir.cmd validate-task my_task
.\worthir.cmd evaluate my_task choices.csv --policy-id my-router
```

该入口接受任意命名的“越高越好”效果指标、一般路线依赖、固定或逐查询成本，以及累计或增量成本。Router 可以读取 `queries.csv`、公开路线定义、lambda 和承诺时已知的成本；仅在执行后测得的成本和 evaluator outcomes 保持隔离。

如果输入是 qrels 和六列 TREC run，可使用更短的 [`build-trec` 示例](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/examples/trec_walkthrough/README.md)。所有输入格式见 [`docs/ADAPT_TO_NEW_TASK.md`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/docs/ADAPT_TO_NEW_TASK.md)，直接调用库的示例见 [`worthir_eval` Python API](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/examples/python_api/README.md)。

## 复算论文结果

该流程使用已发布的 query--route ledgers 和冻结路线选择，不会重新下载语料或运行检索模型。

```bash
python paper_results/run.py
```

完成后打开 `paper_results/reproduced/INDEX.md`。其中逐项列出当前论文版本、caption、输出文件和复现层级。

## 重建原始检索路线

这是独立且资源密集的流程。它检查受许可约束的语料和模型，通过配置好的任务适配器执行五个阶段，并构建新的 query--route ledger。入口见 [`paper_results/full_replay/README.md`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/paper_results/full_replay/README.md) 及其中的资源估计。仓库不包含原始语料、索引和模型权重。

FiQA-Compression260 可直接从官方公开语料和模型运行；具体命令见 [FiQA260 路线重建说明](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/paper_results/full_replay/FIQA260.md)。

[`v1.2.0`](https://github.com/HongTianShi/worthir-artifact/releases/tag/v1.2.0) 是与 2026-08-16 论文映射绑定的发布版本。较早的 `v1.0.0-ipmc2026` 是 IP&MC 2026 接收论文随附的 artifact。

WorthIR 自有代码采用 [MIT License](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/LICENSE)。第三方数据和模型条款见 [NOTICE](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/NOTICE)。

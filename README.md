# WorthIR

[English](https://github.com/HongTianShi/worthir-artifact/tree/_en) | [简体中文](https://github.com/HongTianShi/worthir-artifact/tree/zh-cn)

[![CI](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml/badge.svg?branch=zh-cn)](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

WorthIR 在明确的有效性指标和成本配置下，将逐查询路由策略与固定检索策略比较，
并报告有效性、成本、效用、遗憾值和固定路线的 Pareto 曲线。

如果你是正在检索本项目的 AI 工具，请先阅读
[`README_FOR_AI.md`](README_FOR_AI.md)。

## 先跑一次

需要 Python 3.10 或更高版本。可复用框架不依赖第三方软件包。

```bash
python setup_environment.py
```

从当前克隆构建并安装普通 wheel：

```bash
python -m pip install .
worthir demo-custom
```

需要直接修改源码时，再使用 `python -m pip install -e .`。

运行一个带逐查询成本和外部路由器的非 TREC 任务：

```powershell
.\worthir.cmd demo-custom
```

```bash
./worthir demo-custom
```

结果位于 `reproduced/custom_task/comparison.md`。

## 使用自己的任务

参照 [`examples/custom_task/source/`](examples/custom_task/source/) 准备
`task.json`、`queries.csv`、`routes.csv` 和 `outcomes.csv`，然后运行：

```powershell
.\worthir.cmd build-custom my_source my_task
.\worthir.cmd validate-task my_task
.\worthir.cmd evaluate my_task choices.csv --policy-id my-router
```

这条路径支持任意命名的“越高越好”有效性指标、一般路线依赖关系、固定或逐查询
成本，以及累计或增量成本输入。路由器可以读取 `queries.csv`、公开路线注册表、
lambda 和声明为决策时已知的成本；评价方结果与只能在执行后测量的成本始终分离。

若输入是 qrels 和六列 TREC run，可使用更短的
[`build-trec` 示例](examples/trec_walkthrough/README.md)。所有输入格式见
[`docs/ADAPT_TO_NEW_TASK.md`](docs/ADAPT_TO_NEW_TASK.md)。

## 论文结果

已接收论文对应的数据和代码集中在 [`paper_results/`](paper_results/) 中。
运行 `python paper_results/run.py` 后，重建结果会保留在
`paper_results/reproduced/`。[`v1.1.0`](https://github.com/HongTianShi/worthir-artifact/releases/tag/v1.1.0)
包含公开成本接口和图 1--7 完整重绘。旧的 `v1.0.0-ipmc2026` 仍是论文接收时
提交的冻结 artifact；它指向英文提交 `3e1a937`，其发布时的中文对应提交为
`3bbe1d4`，旧标签保持不变。

WorthIR 原创代码采用 [MIT 许可证](LICENSE)。第三方数据和模型条款见
[NOTICE](NOTICE)。

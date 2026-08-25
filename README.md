# WorthIR

[English](https://github.com/HongTianShi/worthir-artifact/tree/_en) | [简体中文](https://github.com/HongTianShi/worthir-artifact/tree/zh-cn)

[![CI](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml/badge.svg?branch=zh-cn)](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/LICENSE)

WorthIR 在明确的有效性指标、累计路线成本和成本偏好下评价逐查询检索路由。
它将冻结的路由策略与固定路线进行比较，并报告有效性、成本、效用、遗憾和
固定路线 Pareto 曲线。

如果你使用 AI 工具检索本项目，请先阅读 [`README_FOR_AI.md`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/README_FOR_AI.md)。

## 选择复现范围

| 目标 | 入口 | 所需材料 | 得到的结果 |
|---|---|---|---|
| 体验 WorthIR 或评价自定义任务 | PyPI 软件包 | 内置示例或自己的任务 CSV | 可运行的契约检查、评分、比较和组织者分析 |
| 复算论文结果 | 固定版本源码与发布的 query--route ledger | `paper_results/` 中已有文件 | 精确闭合论文中的表格和图片 |
| 重建原始检索路线 | 源码以及外部语料、索引和模型 | FiQA-Compression260 是完整参考实现；其他任务需要注册资源和适配器 | 重新生成 query--route outcomes，再交由 WorthIR 验证 |

## 从零开始

需要 Python 3.10 或更高版本。推荐从 PyPI 安装：

```bash
python -m pip install worthir-eval==1.3.1
worthir demo-custom
```

如果 `worthir` 不在 `PATH` 中，请运行 `python -m worthir demo-custom`。
PyPI wheel 的终端提示为英文；中文命令行请使用下方源码版本。

固定到不可变中文源码：

```bash
git clone --branch v1.3.1-zh-cn --depth 1 https://github.com/HongTianShi/worthir-artifact.git
cd worthir-artifact
./worthir demo-custom
```

Windows 将最后一行换成 `.\worthir.cmd demo-custom`。源码启动器会在首次运行时
创建 `.venv`，无需再执行 PyPI 安装。

成功运行后，终端末尾会出现：

```text
已构建：.../reproduced/custom_task
已写入：.../reproduced/custom_router_choices.csv
请打开：.../reproduced/custom_task/comparison.md
```

生成目录如下：

```text
reproduced/
├── custom_router_choices.csv
└── custom_task/
    ├── contracts/              路线定义和任务契约
    ├── participant/            路由器可见输入与冻结动作
    ├── evaluator/ledger.csv    组织者专用的查询—路线结果
    ├── comparison.csv
    ├── comparison.md
    └── fixed_routes.csv
```

报告同时列出路由器与所有固定路线，例如：

```text
| 策略                | 有效性 | 成本   | 效用   | 相对固定策略的 Delta U |
| example-rule-router | 0.9000 | 0.1507 | 0.8774 | +0.0625                |
```

## 评价自己的任务

复制 [`examples/custom_task/source/`](https://github.com/HongTianShi/worthir-artifact/tree/zh-cn/examples/custom_task/source) 中的四个文件：

- `task.json`：指标、lambda、预先声明的敏感性网格和固定参照；
- `queries.csv`：每个查询一行，只含路线选择时允许使用的信息；
- `routes.csv`：路线名称、前置依赖、成本和开发集选定路线；
- `outcomes.csv`：每个查询—路线对的组织者专用有效性与成本。

构建并检查任务：

```bash
worthir build-custom my_source my_task
worthir validate-task my_task
```

你的路由器而不是 WorthIR 读取 `my_task/participant/`，并生成 `choices.csv`。
最小格式为：

```csv
query_uid,selected_route_id
q001,base
q002,rerank
```

将冻结选择绑定到任务契约，并与所有固定路线比较：

```bash
worthir evaluate my_task choices.csv --policy-id my-router
```

完整路由器示例位于 [`examples/custom_router/`](https://github.com/HongTianShi/worthir-artifact/tree/zh-cn/examples/custom_router)。
若输入是 qrels 和六列 TREC run，请使用 [`build-trec`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/examples/trec_walkthrough/README.md)。
通用输入格式见 [`docs/ADAPT_TO_NEW_TASK.md`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/docs/ADAPT_TO_NEW_TASK.md)。

## 组织者分析

下列命令会将冻结动作与 evaluator ledger 连接。默认输出到
`my_task/organizer_private/`，并拒绝写入 `participant/`：

```bash
worthir analyze my_task --organizer-output my_task/organizer_private/per_query_scores.csv
worthir sensitivity my_task
worthir budget my_task
worthir plot my_task
```

`analyze` 报告逐查询的已选结果、开发集固定参照、oracle 路线、遗憾和机会分层。
`sensitivity` 与 `budget` 默认读取 `task.json` 中的网格；临时命令行网格会标为
非预注册。`plot` 直接输出无需额外绘图库的 SVG Pareto 图。所有结果都标明
`descriptive` 和 `evaluator_only`。CSV 无需额外依赖；安装 `pyarrow` 后也可输出
Parquet。

字段定义见 [`docs/OUTPUTS.md`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/docs/OUTPUTS.md)，安装和下载故障见 [`docs/TROUBLESHOOTING.md`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/docs/TROUBLESHOOTING.md)。

## 复算论文图表

该步骤需要源码，因为发布的查询—路线 ledger 不包含在核心 PyPI wheel 中：

```bash
python paper_results/run.py
```

打开 `paper_results/reproduced/INDEX.md`。其中逐项链接论文图表的输入、命令、
输出和复现层级。

## 重建原始检索路线

本仓库不分发原始语料、索引和模型权重。分阶段重建入口与资源估计见
[`paper_results/full_replay/README.md`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/paper_results/full_replay/README.md)。
FiQA-Compression260 提供公开语料适配器和 CPU 安装流程，见
[`FIQA260.md`](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/paper_results/full_replay/FIQA260.md)。

WorthIR 代码采用 [MIT License](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/LICENSE)。
第三方数据和模型条款见 [NOTICE](https://github.com/HongTianShi/worthir-artifact/blob/zh-cn/NOTICE)。

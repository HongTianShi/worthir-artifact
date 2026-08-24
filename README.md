# WorthIR

[English](https://github.com/HongTianShi/worthir-artifact/tree/_en) | [简体中文](https://github.com/HongTianShi/worthir-artifact/tree/zh-cn)

[![CI](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml/badge.svg?branch=_en)](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/HongTianShi/worthir-artifact/blob/_en/LICENSE)

WorthIR compares query-level routing policies with fixed retrieval strategies
under a declared effectiveness measure and cost profile. It reports
effectiveness, cost, utility, regret, and the fixed-route Pareto curve.

If you are an AI tool, read [`README_FOR_AI.md`](https://github.com/HongTianShi/worthir-artifact/blob/_en/README_FOR_AI.md) before
searching the repository.

## 60-second demo

Python 3.10 or newer is required. Choose one installation path.

**Source archive or Git clone:** run the local launcher. It creates the local
environment when first needed.

```powershell
.\worthir.cmd demo-custom
```

```bash
./worthir demo-custom
```

**PyPI:** install the released package, then use the global command.

```bash
python -m pip install worthir-eval==1.2.1
worthir demo-custom
```

If the `worthir` command is not on `PATH`, use the equivalent module entry:

```bash
python -m worthir demo-custom
```

Do not run both setup paths. Open `reproduced/custom_task/comparison.md` after
the command finishes. The published wheel uses English terminal messages; the
Chinese source branch provides Chinese launchers and documentation.

## Use your own task

Prepare `task.json`, `queries.csv`, `routes.csv`, and `outcomes.csv` as shown in
[`examples/custom_task/source/`](https://github.com/HongTianShi/worthir-artifact/tree/_en/examples/custom_task/source), then run:

```powershell
.\worthir.cmd build-custom my_source my_task
.\worthir.cmd validate-task my_task
.\worthir.cmd evaluate my_task choices.csv --policy-id my-router
```

This path accepts any named higher-is-better effectiveness measure, arbitrary
route prerequisites, fixed or query-dependent costs, and either cumulative or
incremental cost input. The router receives `queries.csv`, the public route
registry, lambda, and any costs declared as known at commitment time. Evaluator
outcomes and costs measured only after execution remain separate.

For qrels and six-column TREC runs, use the shorter [`build-trec` walkthrough](https://github.com/HongTianShi/worthir-artifact/blob/_en/examples/trec_walkthrough/README.md).
All input formats are described in [`docs/ADAPT_TO_NEW_TASK.md`](https://github.com/HongTianShi/worthir-artifact/blob/_en/docs/ADAPT_TO_NEW_TASK.md).
For direct library use, see the
[`worthir_eval` Python example](https://github.com/HongTianShi/worthir-artifact/blob/_en/examples/python_api/README.md).

## Recompute the paper results

This uses released query--route ledgers and frozen route selections. It does
not redownload corpora or rerun retrieval models.

```bash
python paper_results/run.py
```

Open `paper_results/reproduced/INDEX.md`.
The index names the exact paper version, caption, output, and reproduction
level for every main-paper and appendix figure or table.

## Rebuild the original retrieval routes

This is a separate, resource-intensive workflow. It checks licensed corpora
and checkpoints, invokes a configured task adapter, and constructs new
query--route ledgers through five explicit stages. Start with
[`paper_results/full_replay/README.md`](https://github.com/HongTianShi/worthir-artifact/blob/_en/paper_results/full_replay/README.md) and
its task-specific resource estimates. Raw corpora, indexes, and model weights
are not included in this repository.

FiQA-Compression260 is directly runnable from the official public corpus and
models; see the [FiQA260 route-rebuild guide](https://github.com/HongTianShi/worthir-artifact/blob/_en/paper_results/full_replay/FIQA260.md).

WorthIR-authored code is released under the [MIT License](https://github.com/HongTianShi/worthir-artifact/blob/_en/LICENSE). Third-party
data and model terms are listed in [NOTICE](https://github.com/HongTianShi/worthir-artifact/blob/_en/NOTICE).

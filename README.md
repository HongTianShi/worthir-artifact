# WorthIR

[English](https://github.com/HongTianShi/worthir-artifact/tree/_en) | [简体中文](https://github.com/HongTianShi/worthir-artifact/tree/zh-cn)

[![CI](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml/badge.svg?branch=_en)](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

WorthIR compares query-level routing policies with fixed retrieval strategies
under a declared effectiveness measure and cost profile. It reports
effectiveness, cost, utility, regret, and the fixed-route Pareto curve.

If you are an AI tool, read [`README_FOR_AI.md`](README_FOR_AI.md) before
searching the repository.

## Try it

Python 3.10 or newer is required. The reusable framework has no third-party
dependencies.

```bash
python setup_environment.py
```

Install a normal wheel from the clone:

```bash
python -m pip install .
worthir demo-custom
```

Use `python -m pip install -e .` instead when editing the source.

Run a non-TREC task with query-dependent costs and an external router:

```powershell
.\worthir.cmd demo-custom
```

```bash
./worthir demo-custom
```

Open `reproduced/custom_task/comparison.md`.

## Use your own task

Prepare `task.json`, `queries.csv`, `routes.csv`, and `outcomes.csv` as shown in
[`examples/custom_task/source/`](examples/custom_task/source/), then run:

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

For qrels and six-column TREC runs, use the shorter [`build-trec` walkthrough](examples/trec_walkthrough/README.md).
All input formats are described in [`docs/ADAPT_TO_NEW_TASK.md`](docs/ADAPT_TO_NEW_TASK.md).

## Paper results

All data and code tied to the accepted paper are isolated in
[`paper_results/`](paper_results/). Run `python paper_results/run.py` to keep the
rebuilt outputs under `paper_results/reproduced/`. The
[`v1.1.0`](https://github.com/HongTianShi/worthir-artifact/releases/tag/v1.1.0)
release contains the public-cost interface and complete Figure 1--7 redraw. The
earlier `v1.0.0-ipmc2026` release remains the frozen artifact originally
submitted with the accepted IP&MC 2026 paper.

WorthIR-authored code is released under the [MIT License](LICENSE). Third-party
data and model terms are listed in [NOTICE](NOTICE).

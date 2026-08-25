# WorthIR

[English](https://github.com/HongTianShi/worthir-artifact/tree/_en) | [简体中文](https://github.com/HongTianShi/worthir-artifact/tree/zh-cn)

[![CI](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml/badge.svg?branch=_en)](https://github.com/HongTianShi/worthir-artifact/actions/workflows/validate.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/HongTianShi/worthir-artifact/blob/_en/LICENSE)

Use WorthIR to register a retrieval task, validate what a router may see,
compare frozen query-level choices with fixed routes, and compute effectiveness,
cost, utility, regret, and the fixed-route Pareto curve.

If you are an AI tool, read [`README_FOR_AI.md`](https://github.com/HongTianShi/worthir-artifact/blob/_en/README_FOR_AI.md) before searching the repository.

## Choose the reproduction scope

| Goal | Entry point | Required material | Result |
|---|---|---|---|
| Try WorthIR or evaluate a custom task | PyPI package | Built-in demo or your task CSV files | Runnable contract validation, scoring, comparison, and organizer analysis |
| Recompute the paper results | Pinned source tree and released query--route ledgers | Files included under `paper_results/` | Exact closure of the released tables and figures |
| Rebuild original retrieval routes | Source tree plus external corpora, indexes, and models | FiQA-Compression260 is the complete reference implementation; other tasks require their registered resources and an adapter | New query--route outcomes followed by WorthIR validation |

## Start from zero

Python 3.10 or newer is required. The recommended path is PyPI:

```bash
python -m pip install worthir-eval==1.3.1
worthir demo-custom
```

If `worthir` is not on `PATH`, run `python -m worthir demo-custom`.

To use the pinned source tree instead:

```bash
git clone --branch v1.3.1 --depth 1 https://github.com/HongTianShi/worthir-artifact.git
cd worthir-artifact
./worthir demo-custom
```

On Windows, replace the last line with `.\worthir.cmd demo-custom`. The source
launcher creates `.venv` on first use; do not install the PyPI package as an
additional setup step.

A successful run ends with lines like these:

```text
BUILT: .../reproduced/custom_task
WROTE: .../reproduced/custom_router_choices.csv
OPEN: .../reproduced/custom_task/comparison.md
```

It creates:

```text
reproduced/
├── custom_router_choices.csv
└── custom_task/
    ├── contracts/              route definitions and task contract
    ├── participant/            legal router inputs and frozen actions
    ├── evaluator/ledger.csv    organizer-only query--route outcomes
    ├── comparison.csv
    ├── comparison.md
    └── fixed_routes.csv
```

The report includes the router and every fixed route, for example:

```text
| Policy              | Effectiveness | Cost   | Utility | Delta U vs. fixed |
| example-rule-router | 0.9000        | 0.1507 | 0.8774  | +0.0625           |
```

## Evaluate your own task

Copy the four files in [`examples/custom_task/source/`](https://github.com/HongTianShi/worthir-artifact/tree/_en/examples/custom_task/source):

- `task.json`: metric, lambda, declared sensitivity grids, and fixed reference;
- `queries.csv`: one row per query with only information legal at route-selection time;
- `routes.csv`: route labels, prerequisites, costs, and the development-selected route;
- `outcomes.csv`: organizer-only effectiveness and cost for every query--route pair.

Build and check the task:

```bash
worthir build-custom my_source my_task
worthir validate-task my_task
```

Your router—not WorthIR—reads `my_task/participant/` and writes `choices.csv`.
The minimum format is:

```csv
query_uid,selected_route_id
q001,base
q002,rerank
```

Bind those frozen choices to the task contract and compare them with all fixed
routes:

```bash
worthir evaluate my_task choices.csv --policy-id my-router
```

The complete router example is under [`examples/custom_router/`](https://github.com/HongTianShi/worthir-artifact/tree/_en/examples/custom_router).
For qrels and six-column TREC runs, use [`build-trec`](https://github.com/HongTianShi/worthir-artifact/blob/_en/examples/trec_walkthrough/README.md).
All generic input formats are documented in [`docs/ADAPT_TO_NEW_TASK.md`](https://github.com/HongTianShi/worthir-artifact/blob/_en/docs/ADAPT_TO_NEW_TASK.md).

## Organizer analyses

These commands join frozen actions with the evaluator ledger. They default to
`my_task/organizer_private/` and refuse to write under `participant/`:

```bash
worthir analyze my_task --organizer-output my_task/organizer_private/per_query_scores.csv
worthir sensitivity my_task
worthir budget my_task
worthir plot my_task
```

`analyze` reports selected outcomes, the development-fixed reference, oracle
route, regret, and opportunity stratum for each query. `sensitivity` and
`budget` use the grids declared in `task.json`; a command-line grid is labeled
non-prespecified. `plot` writes a dependency-free SVG Pareto chart. Every
output is marked `descriptive` and `evaluator_only`. Parquet output is available
when `pyarrow` is installed; CSV requires no extra package.

See [`docs/OUTPUTS.md`](https://github.com/HongTianShi/worthir-artifact/blob/_en/docs/OUTPUTS.md) for field definitions and [`docs/TROUBLESHOOTING.md`](https://github.com/HongTianShi/worthir-artifact/blob/_en/docs/TROUBLESHOOTING.md) for installation and download failures.

## Recompute the paper tables and figures

This step requires a source checkout because the released query--route ledgers
are not part of the core PyPI wheel:

```bash
python paper_results/run.py
```

Open `paper_results/reproduced/INDEX.md`. It links every paper figure and table
to its input, command, output, and reproduction level.

## Rebuild retrieval routes

Raw corpora, indexes, and model weights are not distributed here. The staged
rebuild interface and resource estimates are in
[`paper_results/full_replay/README.md`](https://github.com/HongTianShi/worthir-artifact/blob/_en/paper_results/full_replay/README.md).
FiQA-Compression260 has a runnable public-corpus adapter and a CPU installation
path in [`FIQA260.md`](https://github.com/HongTianShi/worthir-artifact/blob/_en/paper_results/full_replay/FIQA260.md).

WorthIR code uses the [MIT License](https://github.com/HongTianShi/worthir-artifact/blob/_en/LICENSE).
Third-party data and model terms are listed in [NOTICE](https://github.com/HongTianShi/worthir-artifact/blob/_en/NOTICE).

# WorthIR

WorthIR evaluates whether a retrieval system should use a more expensive route
for each query. It reports effectiveness, cost, utility, regret, fixed-route
baselines, and the fixed-route Pareto curve.

If you are an AI tool, read [`README_FOR_AI.md`](README_FOR_AI.md) before
searching the repository.

## Setup

Python 3.10 or newer is required. The reusable framework has no third-party
dependencies.

```bash
python setup_environment.py
```

Then run the complete example:

```powershell
.\worthir.cmd demo
```

```bash
./worthir demo
```

Open `reproduced/trec_walkthrough/comparison.md` to see the result.

## Use your retrieval runs

Prepare one folder containing qrels, TREC runs, route definitions, and costs as
shown in [`examples/trec_walkthrough/source/`](examples/trec_walkthrough/source/).
Then run:

```powershell
.\worthir.cmd build-trec my_source my_task --task-id my-task --metric ndcg@10 --lambda 0.08
.\worthir.cmd compare my_task
```

Use `./worthir` instead of `.\worthir.cmd` on macOS or Linux. Input formats,
query-dependent costs, additional policies, and the meaning of lambda are
explained in [`docs/ADAPT_TO_NEW_TASK.md`](docs/ADAPT_TO_NEW_TASK.md).

## Paper results

The exact data and code behind the paper are isolated in
[`paper_results/`](paper_results/). They are not needed to apply WorthIR to a
new task.

WorthIR-authored code is released under the MIT License.

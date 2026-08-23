# Results for the 2026-08-16 paper

**Paper:** *WorthIR: An Evaluation Protocol for Cost-Aware Retrieval Routing*

**Paper version:** 2026-08-16 submission

**Released artifact:** [v1.2.0](https://github.com/HongTianShi/worthir-artifact/releases/tag/v1.2.0)

Run:

```bash
python run.py
```

This recomputes the paper results from released query--route ledgers, frozen
route selections, and frozen diagnostic summaries. It does not download raw
corpora, rebuild indexes, train retrieval models, or rerun route inference.
The local environment is installed from `requirements-lock.txt`, which fixes
and verifies every direct and transitive package; `requirements.txt` remains
the short human-readable source list.

The command keeps:

- `reproduced/INDEX.md`: one clickable index for every paper figure and table;
- `reproduced/paper/figure1.pdf` through `figure7.pdf`;
- `reproduced/paper/table1.csv` through `table6.csv`;
- appendix files named by their paper labels, such as
  `appendix_figure_e1.pdf` and `appendix_table_e1.csv`;
- `reproduced/rqs/`: supporting RQ2--RQ5 readouts;
- `reproduced/validation.json`: commands, timings, and final status.

## What each result means

| Item | Caption or subject | Output | Reproduction level |
| --- | --- | --- | --- |
| Figure 1 | WorthIR evaluation protocol | `figure1.pdf` | Frozen manuscript asset export |
| Figure 2 | Effectiveness--cost profiles | `figure2.pdf` | Complete redraw |
| Figure 3 | FEVER utility decomposition | `figure3.pdf` | Complete redraw and arithmetic closure |
| Figure 4 | Routing-opportunity contributions | `figure4.pdf` | Complete redraw |
| Figure 5 | Cost-preference sensitivity | `figure5.pdf` | Complete redraw |
| Figure 6 | Where FEVER reranking creates value | `figure6.pdf` | Complete redraw |
| Figure 7 | FEVER warm-online systems audit | `figure7.pdf` | Complete redraw |
| Table 1 | Tasks, routes, and measures | `table1.csv` | Frozen task-specification export |
| Table 2 | Fixed-strategy preference under cost | `table2.csv` | Per-query recomputation and diagnostic closure |
| Table 3 | Cross-task routing comparison | `table3.csv` | Released-action aggregation and Holm-test closure |
| Table 4 | FEVER matched route sets | `table4.csv` | Frozen-action summary |
| Table 5 | Recoverable opportunity | `table5.csv` | Arithmetic closure |
| Table 6 | Association with route-specific utility | `table6.csv` | Held-out summary closure |

Exact captions, appendix items, and file requirements are in
[`PAPER_SPEC.json`](PAPER_SPEC.json). The human-readable input-to-output map is
[`PAPER_MAP.md`](PAPER_MAP.md).

## Directory contents

- `analyses/`: released RQ2--RQ5 action files and summaries;
- `replays/`: task ledgers and task-specific scorers;
- `paper_reproduction/`: manuscript inputs, figures, and builders;
- `full_replay/`: raw-route reconstruction entry points and resource notes;
- `docs/`: data terms and evaluator semantics.

Large corpora, indexes, model weights, and raw rankings are not included.

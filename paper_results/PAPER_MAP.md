# Paper result map

This map applies only to:

- **Paper:** *WorthIR: An Evaluation Protocol for Cost-Aware Retrieval Routing*
- **Version:** 2026-08-16 submission
- **Artifact release:** [v1.2.1](https://github.com/HongTianShi/worthir-artifact/releases/tag/v1.2.1)

`PAPER_SPEC.json` is the machine-readable source of truth. `python run.py`
checks that every item below is produced and writes a clickable
`reproduced/INDEX.md`.

## Main paper

| Paper item | Primary released input | Output | Reproduction level |
| --- | --- | --- | --- |
| Figure 1 | `paper_reproduction/assets/figure1.png` | `reproduced/paper/figure1.pdf` | Frozen manuscript asset export |
| Figure 2 | TREC-DL and structured route ledgers; FEVER frozen actions; FiQA diagnostic results | `reproduced/paper/figure2.pdf` | Complete redraw |
| Figure 3 | `paper_reproduction/inputs/figure3_decomposition.csv` | `reproduced/paper/figure3.pdf` | Complete redraw and arithmetic closure |
| Figure 4 | `analyses/rq3_utility_sources/data/query_strata.csv` | `reproduced/paper/figure4.pdf` | Complete redraw |
| Figure 5 | `analyses/rq4_robustness/data/cost_preference_curves.csv` | `reproduced/paper/figure5.pdf` | Complete redraw |
| Figure 6 | `analyses/rq5_route_value/data/rq5_fever_gold_rank_band_routes.csv` | `reproduced/paper/figure6.pdf` | Complete redraw |
| Figure 7 | FEVER latency and matched-policy results | `reproduced/paper/figure7.pdf` | Complete redraw |
| Table 1 | Registered task and route descriptions | `reproduced/paper/table1.csv` | Frozen task-specification export |
| Table 2 | TREC-DL query--route ledgers and FiQA diagnostic results | `reproduced/paper/table2.csv` | Per-query recomputation and diagnostic closure |
| Table 3 | Cross-task policy summaries and Holm tests | `reproduced/paper/table3.csv` | Released-action aggregation and test closure |
| Table 4 | FEVER matched-route-set results | `reproduced/paper/table4.csv` | Frozen-action summary and manuscript-interval check |
| Table 5 | `paper_reproduction/inputs/table3_recoverability.csv` | `reproduced/paper/table5.csv` | Arithmetic closure |
| Table 6 | Held-out route-value summaries | `reproduced/paper/table6.csv` | Summary closure |

Table numbers refer to the 2026-08-16 paper. Internal RQ filenames are not
paper table numbers.

## Appendix

Appendix outputs use paper labels directly:

- Tables A.1--A.2: `appendix_table_a1.csv`, `appendix_table_a2.csv`
- Tables B.1--B.2: `appendix_table_b1.csv`, `appendix_table_b2.csv`
- Table C.1: `appendix_table_c1.csv`
- Tables D.1--D.2: `appendix_table_d1.csv`, `appendix_table_d2.csv`
- Tables E.1--E.6: `appendix_table_e1.csv` through `appendix_table_e6.csv`
- Figures E.1--E.2: `appendix_figure_e1.pdf`, `appendix_figure_e2.pdf`
- Figures F.1--F.2: `appendix_figure_f1.pdf`, `appendix_figure_f2.pdf`

The generated `reproduced/INDEX.md` records the caption, output, status, and
reproduction level for every item.

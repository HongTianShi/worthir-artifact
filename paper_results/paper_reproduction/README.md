# Paper result reproduction

This package rebuilds Figures 1–7 and Tables 2–4 from compact released inputs.
It performs no route inference, fitting, or model selection.

```bash
python scripts/reproduce_paper.py --output-dir reproduced/paper
```

- Figure 1 uses one TREC-DL 2019 protocol example.
- Figure 2 validates the FiQA-Compression260 route coordinates.
- Figure 3 plots within-task fixed-to-oracle recovery.
- Figure 4 shows the utility contributions of the three opportunity strata.
- Figure 5 redraws the cost-preference sensitivity curves.
- Figure 6 localizes FEVER reranking gains by first relevant rank.
- Figure 7 compares FEVER warm-online latency with utility.
- Table 2 is recomputed from the complete TREC-DL menu ledgers.
- Table 3 validates gain and recovered-headroom identities.
- Table 4 is reaggregated from the matched-budget query-level audit.

The validation checks plotted coordinates, table arithmetic, row counts, and
generated-file presence.

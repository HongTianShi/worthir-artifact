# Paper result reproduction

This package rebuilds Figures 1–3 and Tables 2–4 from compact released inputs.
It performs no route inference, fitting, or model selection.

```bash
python scripts/reproduce_paper.py --output-dir reproduced/paper
```

- Figure 1 uses one TREC-DL 2019 protocol example.
- Figure 2 validates the FiQA-Compression260 route coordinates.
- Figure 3 plots within-task fixed-to-oracle recovery.
- Table 2 is recomputed from the complete TREC-DL menu ledgers.
- Table 3 validates gain and recovered-headroom identities.
- Table 4 is reaggregated from the matched-budget query-level audit.

The validation checks source hashes, plotted coordinates, table arithmetic,
row counts, and generated-file presence. PDF byte hashes may vary across font
and plotting backends.

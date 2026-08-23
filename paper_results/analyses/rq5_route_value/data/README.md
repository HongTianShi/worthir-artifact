# RQ5 Route-Value Diagnostics

These CSV files support the analysis of which inference-time signals are associated with route-specific utility gain. They cover route-value prediction, within-difficulty associations, difficulty-band heterogeneity, information-block contrasts, operation controls, FEVER gold-rank bands, question-type profiles, and complementarity summaries.

Several fields are evaluator-only diagnostics and must not be described as router inputs. The analyses are associative rather than causal; use the terminology and rounding documented in the result tables.

`python paper_results/run.py` checks these released summaries and copies the
main predictability and operation-control tables to
`paper_results/reproduced/rqs/`. Figure 6 and Table 6 mappings are listed in
`paper_results/PAPER_MAP.md`.

# MuSiQue dependence-unit audit

- Exact official-validation mean contrast: 0.013970.
- Resampling scope: conditional stability on the fixed 2,417-query official-validation ledger, not query-superpopulation coverage.

| Component definition | components | largest | shared-query share | cluster-bootstrap 95% range |
|---|---:|---:|---:|---:|
| support_title | 415 | 690 | 91.23% | [0.003976,0.029116] |
| support_paragraph_text | 528 | 84 | 90.28% | [0.001762,0.026014] |
| decomposition_question | 321 | 433 | 96.73% | [0.000950,0.026266] |
| union | 179 | 1437 | 98.35% | [0.007650,0.033091] |

Query bootstrap: [0.006425,0.021461].

The union component is the strictest audited dependence unit. Its interval is the primary stability readout when reported beside the exact finite-ledger mean.

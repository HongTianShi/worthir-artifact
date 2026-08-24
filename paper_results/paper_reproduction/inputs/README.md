# Paper-Reproduction Input Authority

| Readout | Input | Validation level |
| --- | --- | --- |
| Figure 1 | `../figures/hero_example_2019.json` plus bound TREC assets | Frozen diagnostic example with file and record lineage |
| Figure 2 | `../figures/cost_quality_inversion_data.csv` | Coordinate and fingerprint validation |
| Figure 3 | `../figures/recoverability_bridge_data.csv` | Within-task normalized plot coordinates |
| Table 2 | `replays/canonical_trec/organizer_private/data/test/*/route_outcomes.parquet` | Recomputed from the per-query complete-menu ledger with the paper's tie-aware quality-oracle rule |
| Table 3 | `table3_recoverability.csv` | Arithmetic identities for gains and headroom; native action scoring where distributed |
| Table 4 | `table4_query_level.parquet` | Reaggregated from 12,000 frozen query rows |

The former exploratory TREC task-health JSON used naive first-argmax tie
handling and is intentionally excluded. It must not be used for the paper's
13/43 and 14/54 disagreement counts.
These compact inputs rebuild Tables 3 and 4 without rerunning retrieval.
`table3_recoverability.csv` contains the reported task-level recovery values;
`table4_query_level.parquet` is reaggregated at query level and checked against
`table4_expected.csv`.

Run `python paper_results/run.py` and open
`paper_results/reproduced/paper/`. See `paper_results/PAPER_MAP.md` for the
paper-to-file mapping and the reproduction level of each result.

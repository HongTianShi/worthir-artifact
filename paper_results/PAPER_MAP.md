# Paper result map

Run `python run.py` in this directory first. The command writes the paths shown
below under `reproduced/`.

| Paper item | Released input | Generator or check | Persistent output | Reproduction level |
| --- | --- | --- | --- | --- |
| Figure 1 | `paper_reproduction/figures/hero_example_2019.json` | `scripts/reproduce_paper.py` | `reproduced/paper/figures/figure1.pdf` | Complete redraw |
| Figure 2 | `paper_reproduction/figures/cost_quality_inversion_data.csv` | `scripts/reproduce_paper.py` | `reproduced/paper/figures/cost_quality_final.png` | Complete redraw |
| Figure 3 | `paper_reproduction/figures/recoverability_bridge_data.csv` | `scripts/reproduce_paper.py` | `reproduced/paper/figures/recoverability_bridge.png` | Complete redraw |
| Figure 4 | `analyses/rq3_utility_sources/data/query_strata.csv` | `scripts/reproduce_rqs.py` | `reproduced/rqs/rq3_query_strata.csv` | Numerical closure; final artwork is not redrawn |
| Figure 5 | `analyses/rq4_robustness/data/cost_preference_summary.csv` | `scripts/reproduce_rqs.py` | `reproduced/rqs/rq4_cost_preference.csv` | Numerical closure; final artwork is not redrawn |
| Figure 6 | `analyses/rq5_route_value/data/rq5_fever_gold_rank_band_routes.csv` | RQ5 checks in `scripts/reproduce_rqs.py` | `reproduced/rqs/reproduction_report.json` | Source-table validation; final artwork is not redrawn |
| Figure 7 | `analyses/rq2_policy_comparison/results/fever_online_latency.csv` | RQ2 checks in `scripts/reproduce_rqs.py` | `reproduced/rqs/reproduction_report.json` | Source-table validation; final artwork is not redrawn |
| Table 2 | Complete TREC-DL route ledgers | `scripts/reproduce_paper.py` | `reproduced/paper/table2_canonical_heldout.csv` | Per-query recomputation |
| Table 3 | `paper_reproduction/inputs/table3_recoverability.csv` | `scripts/reproduce_paper.py` | `reproduced/paper/table3_recoverability.csv` | Arithmetic recomputation |
| Table 4 | `paper_reproduction/inputs/table4_query_level.parquet` | `scripts/reproduce_paper.py` | `reproduced/paper/table4_matched_top10.csv` | Query-level reaggregation |
| Table 5 | `analyses/rq2_policy_comparison/results/fever_same_menu_policy_comparison.csv` | `scripts/reproduce_rqs.py` | `reproduced/rqs/rq2_fever_same_menu.csv` | Released-action rescoring and table check |
| Table 6 | `analyses/rq5_route_value/data/rq5_route_value_prediction_summary.csv` | RQ5 checks in `scripts/reproduce_rqs.py` | `reproduced/rqs/rq5_prediction_summary.csv` | Numerical closure from released predictions |

## Appendix results

The appendix analyses are grouped by research question rather than by page:

| Result family | Repository location | What can be rerun locally |
| --- | --- | --- |
| Matched policies, random controls, and FEVER latency | `analyses/rq2_policy_comparison/` | Released action vectors are rescored against released route outcomes |
| Utility-source strata and switching analyses | `analyses/rq3_utility_sources/` | Published summaries and their arithmetic checks |
| Cost preference, route recurrence, and learner checks | `analyses/rq4_robustness/` | Published summaries and their closure checks |
| Evidence depth, structured controls, and predictability | `analyses/rq5_route_value/` | Published summaries and their closure checks |
| Released evaluator bundles | `replays/` | Ledger integrity and scoring without rerunning retrieval |
| Retrieval from raw corpora and model inference | `full_replay/` | Documented resource-heavy procedure; data and model downloads are not bundled |

“Numerical closure” means that the released values and identities used in the
paper are checked, but the publication graphic itself is not regenerated. This
distinction prevents a source-table check from being mistaken for a full redraw.

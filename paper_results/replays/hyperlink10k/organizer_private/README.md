# WorthIR Hyperlink10k organizer-private scorer

`raw_outcomes.parquet` stores the complete 10,000 x 5 raw outcome matrix.
Utility, oracle action, and exact within-menu regret are recomputed by the
scorer from raw NDCG@4 and the bound public cost contract. Candidate/evidence
fingerprints derive mechanically from the official first-10k source rows and
the three frozen hyperlink caches; no model or retrieval execution is used.

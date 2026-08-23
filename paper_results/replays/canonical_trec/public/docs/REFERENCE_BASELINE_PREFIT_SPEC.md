# Canonical Task Reference Baselines — Prefit Specification

## Purpose

Calibrate the submission/evaluator path with two ordinary, non-proposed
adaptive baselines. These baselines do not define WorthIR and are not used to
change the task, menu, costs, metric, or claims.

Both baselines may read:

- public development legal state;
- public development complete-menu outcomes;
- public held-out legal state;
- frozen route and cost contracts.

They may not read organizer-only held-out outcomes before producing their
submission files.

## Shared features

The predictor feature vector is frozen to eight scalar legal fields:

1. `query_character_count`;
2. `query_whitespace_token_count`;
3. `query_digit_count`;
4. `query_punctuation_count`;
5. `bm25_top_score`;
6. `bm25_score_mean`;
7. `bm25_score_std`;
8. `bm25_top1_top2_margin`.

Dataset identity, document IDs, qrels, paid-route scores, outcomes, utility,
regret, oracle actions, and test-selected quantities are excluded.

## B1: BM25-margin QPP gate

- Action set: `stop_bm25` or `cross_encoder`.
- Rule: purchase `cross_encoder` when
  `bm25_top1_top2_margin <= threshold`; otherwise stop at BM25.
- Candidate thresholds: unique development quantiles for
  `q = 0, .01, ..., 1`, plus the two constant-action endpoints.
- Selection: maximize mean development
  `NDCG@10 - .08 C_op`.
- Tie break: lower cross-encoder buy rate, then lower threshold.
- The selected threshold is frozen before the held-out submission is scored.

## B2: ExtraTrees view-quality regressor

- Target: four raw NDCG@10 values, ordered by the frozen route registry.
- Estimator: `ExtraTreesRegressor`.
- Hyperparameters:
  - `n_estimators=200`;
  - `min_samples_leaf=20`;
  - `max_features=1.0`;
  - `bootstrap=False`;
  - `random_state=20260728`;
  - `n_jobs=-1`.
- No hyperparameter search, calibration, or test-conditioned fitting.
- Decision: choose the first route in registered order maximizing
  `predicted_raw_ndcg_at_10 - .08 C_op`.

## Reporting

After actions are written, the scorer reports both
years separately. Null or adverse results are retained. No baseline result may
change this specification or the canonical task contract.

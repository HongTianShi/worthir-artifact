# MuSiQue--WorthIR result summary

## Status

**FULL PASS:** MuSiQue satisfies the complete WorthIR structured-family task
criteria. All preregistered gates G0--G5 pass without changing membership,
routes, features, costs, learner family, thresholds, or official-validation
queries after outcomes were produced.

## Evaluation surface

- 22,355 unique answerable questions: 15,950 train, 3,988 development, and
  2,417 official-validation questions used as test.
- Four paragraph-retrieval routes with complete query--route outcomes and
  per-query operator-counted costs.
- Separate legal-state, private evidence, private qrel, outcome, ranking,
  policy-state, and candidate-fingerprint layers.
- 89,420 query--route rankings and 7,251 registered control outcomes.
- Development-only learner selection followed by one frozen
  official-validation evaluation.
- Ranking and metric recomputation plus an empty-directory replay.

## Main results

| Quantity | Result |
|---|---:|
| `F_dev` route | V2 paragraph |
| `F_dev` test utility | 0.505436 |
| `F_TIH` route | V2 paragraph |
| `A_dev` test utility | 0.519406 |
| `O_TIH` test utility | 0.629182 |
| `A_dev - F_dev` | **0.013970** |
| paired 95% CI | **[0.006425, 0.021461]** |
| fixed-to-oracle utility headroom | 0.123745 |
| recoverability | **11.29%** |
| raw NDCG headroom | 0.116081 |
| route top-1 disagreement | 68.23% |

Every route receives at least 5% fractional raw-effectiveness oracle share.
V0 and V2 exceed 10% utility-oracle share. All six registered hop strata have
fixed-to-oracle utility headroom above 0.04.

## Target and control fidelity

Real paragraph scoring beats the within-query shuffled-score control by
0.353732 NDCG@4, with 95% CI `[0.339202, 0.367922]`. Real decomposition
conditioning beats the matched wrong-decomposition control by 0.076853, with
95% CI `[0.067733, 0.085821]`.

These controls show that the task responds to paragraph content and
query-matched decomposition structure rather than route labels, candidate
counts, or deterministic tie behavior.

## Evaluation design

The task uses all 22,355 answerable source questions, preserves the official
validation split as test, evaluates source paragraph IDs, records per-query
operator-counted costs, separates development selection from test scoring,
and retains ranking arrays, fingerprints, controls, and an independent replay.

## Interpretation boundaries

- MuSiQue provides a same-family structured replication under a legal state
  that includes released decomposition questions.
- The evaluated policy recovers a positive 11.29% of held-out utility
  headroom; this is not an information-theoretic limit.
- The result does not show that structured evidence causally creates
  recoverability or that all learners will behave similarly.
- The policy requires the released decomposition fields and is not a raw-query
  deployment result.
- The baseline learner is an evaluation comparator rather than a proposed
  method.

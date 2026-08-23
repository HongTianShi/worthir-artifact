# WorthIR--FEVER full evaluation

**Status: complete (13,332 outcome-separated test queries).**

## Fixed routes

|        |   raw_ndcg_10 |   recall_10 |   complete_set_recall_10 |   mean_cost_work |
|:-------|--------------:|------------:|-------------------------:|-----------------:|
| bm25   |      0.660222 |    0.808883 |                 0.803105 |        0         |
| bi200  |      0.613253 |    0.798328 |                 0.793579 |        0.509272  |
| ce20   |      0.783193 |    0.846823 |                 0.840684 |        0.0670486 |
| ce100  |      0.815562 |    0.897155 |                 0.893864 |        0.324833  |
| hybrid |      0.779608 |    0.849653 |                 0.845785 |        0.565902  |

## Headline WorthIR readout (`lambda=.08`)

- `F_dev`: 0.789576 via `ce100`.
- `F_TIH`: 0.789576 via `ce100` (nondeployable).
- `A_dev`: 0.800717.
- `O_TIH`: 0.860474 (evaluator-only).
- Deployable delta and 95% paired bootstrap interval:
  0.011141
  [0.009722, 0.012503].
- Conservative delta and interval:
  0.011141
  [0.009776, 0.012543].
- Empirical recoverability: kappa_dev=15.71%,
  kappa_TIH=15.71%.

## Interpretation boundary

This full result tests the registered WorthIR contract on fact-verification
document retrieval.  It is retrospective and outcome-separated.  It does not
turn the measurement-probe learner into a proposed method and does not claim
prospective deployment validity or an information-theoretic limit.

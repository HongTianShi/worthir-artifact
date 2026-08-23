# WorthIR--FEVER result summary

Date: 2026-07-31  
Status: **PASS**

## Scope

FEVER is a fact-verification document-retrieval task over a 5.4-million-page
corpus, with a common BM25 parent and four heterogeneous reranking routes. The
same buy-before-score contract covers sparse retrieval, dense reranking,
cross-encoder depth, and a hybrid route over one document universe. Primary
cost is qrel-independent tokenizer work; a warm-latency profile provides a
separate hardware-qualified check.

## Main result

At the registered preference `lambda=0.08`:

| Quantity | Value |
|---|---:|
| `F_dev` (`CE-100`) | 0.789576 |
| `F_TIH` (`CE-100`) | 0.789576 |
| `A_dev` | 0.800717 |
| `O_TIH` | 0.860474 |
| `A_dev - F_dev` | **0.011141** |
| paired 95% CI | **[0.009722, 0.012503]** |
| `A_dev - F_TIH` | **0.011141** |
| conservative 95% CI | **[0.009776, 0.012543]** |
| fixed-to-oracle headroom | 0.070898 |
| empirical recovery `kappa_dev=kappa_TIH` | **15.71%** |

`F_dev` and `F_TIH` select the same route at every registered preference, so
the adaptive gain does not depend on weakening the fixed baseline.

## Preference sensitivity

| lambda | Fixed route | Adaptive delta | 95% CI | kappa |
|---:|---|---:|---|---:|
| 0 | CE-100 | -0.000912 | [-0.002299, 0.000531] | -1.80% |
| 0.02 | CE-100 | 0.001060 | [-0.000374, 0.002466] | 1.90% |
| 0.04 | CE-100 | 0.003747 | [0.002326, 0.005148] | 6.16% |
| 0.08 | CE-100 | 0.011141 | [0.009722, 0.012503] | 15.71% |
| 0.16 | CE-20 | 0.018554 | [0.015814, 0.021408] | 22.54% |

Adaptation is not justified when acquisition is free, becomes measurable at
moderate cost, and grows as evidence work receives greater weight in this
task.

## Route heterogeneity

At `lambda=0.08`, the evaluator-only oracle selects BM25 for 7,665 queries
(57.49%), CE-20 for 4,061 (30.46%), CE-100 for 690 (5.18%), bi-200 for 624
(4.68%), and hybrid for 292 (2.19%).

The evaluated policy selects BM25 for 1,410, CE-20 for 6,651, CE-100 for
5,055, and hybrid for 216 queries. It matches the oracle for 3,638 queries but
still makes 6,311 unnecessary purchases and 3,327 wrong-paid-route choices.
Mean remaining regret is 0.05976.

## Cost and effectiveness

Fixed mean effectiveness rises from 0.6602 for BM25 to 0.7832 for CE-20 and
0.8156 for CE-100. Their registered mean incremental costs are 0, 0.0670, and
0.3248. The warm-latency audit places the same routes on the mean, median, and
p95 Pareto curves and finds bi-200 and hybrid dominated.

## Interpretation boundaries

- FEVER provides one retrospective task with a distinct corpus, target,
  available routes, and error structure; it does not establish universal
  validity across IR tasks.
- The registered policy has a positive, precisely estimated adaptive gain but
  is not presented as a new state-of-the-art retrieval method.
- The preference sweep identifies where adaptation becomes useful on FEVER;
  it does not imply the same trend on every task.
- The measured millisecond values are specific to the registered hardware and
  are not universal deployment costs.

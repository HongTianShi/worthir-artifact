# RQ5: Route-Specific Marginal Value

RQ5 separates query difficulty from the marginal utility of a particular
retrieval operation. The compact files cover three mechanisms.

- **Candidate reach and reranking depth.** FEVER rows group queries by the rank
  of the first relevant evidence page in the BM25 list. A route helps when its
  reranking depth reaches that page; no paid route can recover a relevant page
  absent from the shared top-200 pool.
- **Operation--failure fit.** On 2Wiki-Structured, real graph expansion is
  compared with degree-matched random and shuffled controls. On MuSiQue, real
  decomposition content is compared with shuffled or wrong decompositions.
- **Predictability at routing time.** Query features, first-stage
  score-distribution features, and their combination are evaluated for
  route-specific marginal utility prediction. Evaluator-only difficulty is
  reported separately and is never a router input.

The machine-readable task label `Structured-v2` is the historical identifier
for 2Wiki-Structured. All files are post-outcome mechanism diagnostics and do
not establish causal effects.

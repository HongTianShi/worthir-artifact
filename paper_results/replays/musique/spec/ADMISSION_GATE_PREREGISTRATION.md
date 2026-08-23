# MuSiQue-WorthIR official-validation admission gate

Specification ID: `musique-worthir-admission-v1.0`  
Status: **frozen before official-validation route outcomes**

## 1. Evaluation object

Given a MuSiQue question, its decomposition questions, and a local paragraph
title sketch, a policy chooses one complete retrieval route before support
labels or paid route outcomes are visible. The evaluator then scores the chosen
paragraph ranking against hidden supporting paragraph IDs.

The task evaluates evidence acquisition, not answer generation.

## 2. Legal state

Policy-visible fields are:

- question;
- decomposition-question text, but not decomposition answers or support IDs;
- paragraph titles and paragraph IDs;
- number of paragraphs and decomposition steps;
- question/decomposition/title length statistics;
- paragraph-length metadata exposed by the local index;
- base title-retrieval score top, margin, and entropy;
- query/title lexical-overlap summaries;
- declared route descriptors and operator-counted costs.

Evaluator-only fields include:

- `is_supporting`;
- answer and answer aliases;
- decomposition answers;
- decomposition support paragraph IDs;
- V1--V3 scores and rankings;
- per-route quality, utility, oracle, and regret;
- test-selected references.

## 3. Four-route menu

All routes rank the same local paragraph IDs. BM25 uses `k1=1.2`, `b=.75`,
lower-cased alphanumeric tokens, and deterministic paragraph-ID tie breaks.

### V0 — base title retrieval

Original question against paragraph titles, plus a `.50` normalized
query/title overlap term. This is the free base route.

### V1 — decomposition-conditioned title retrieval

Original and decomposition questions against titles, plus `.25` of V0.
Parent: V0.

### V2 — full-paragraph retrieval

Original question against `title + paragraph text`, plus `.15` of V0.
Parent: V0.

### V3 — decomposition-conditioned paragraph retrieval

Original plus decomposition questions against full paragraphs, plus `.30` of
the maximum per-decomposition paragraph score and `.15` of V2.
Parents: V1 and V2.

The previously explored `full_context` mixture is excluded because it does not
purchase a distinct representation beyond V3. CE is excluded from this bounded
gate; it is an optional later menu expansion, not needed to admit the core task.

## 4. Operator-counted cost

Costs use only purchase-time-visible counts. For query \(q\), let \(T_q\) be
the total title-token count, \(P_q\) the total indexed paragraph-token count,
and \(d_q\) the number of decomposition questions. Define:

- `work(V0)=0`;
- `work(V1)=d_q T_q`;
- `work(V2)=P_q`;
- `work(V3)=d_q T_q + (1+d_q)P_q`.

Per-query normalized cost is `work(v)/work(V3)`. V3 therefore costs one; the
other routes retain their actual relative operator work. This is the primary
Operator-counted profile. The earlier hand-declared `.00/.04/.16/.30` profile
is reported only as sensitivity.

Headline utility is `NDCG@4 - .08 * normalized_operator_cost`.

## 5. Metrics and references

Primary quality: paragraph-ID NDCG@4.  
Secondary: Recall@4, F1@4, support-title recall@4, operator work, warm latency.

- `F_dev`: fixed route selected by development mean utility;
- `F_TIH`: test-in-hindsight fixed reference, diagnostic only;
- `A_dev`: train-fitted learner family selected by development utility and
  frozen before official-validation scoring;
- `O_TIH`: per-query evaluator oracle.

The valid learner family contains RF, ExtraTrees, and histogram gradient
boosting utility regressors. They use only the legal features above plus
route one-hot/descriptor fields. No paid-route score is a predictor.

## 6. Registered controls

On official validation:

1. shuffled-paragraph control: deterministically permute V2 scores within each
   query;
2. wrong-decomposition control: replace the decomposition text by another test
   query with the same decomposition count, selected by a frozen hash cycle;
3. random ranking: deterministic paragraph-ID permutation.

Controls retain the corresponding real-route cost.

## 7. Gates

All confidence intervals are paired 10,000-replicate query bootstraps with seed
`20260730`.

### G0 — integrity

- exact registered membership and zero official split overlap;
- every gold/decomposition ID resolves;
- all legal/evaluator fields remain separated;
- every query-route result is a complete deterministic paragraph-ID ranking;
- metric, ranking, source, and code hashes reproduce.

### G1 — menu heterogeneity

- at least three routes each receive at least 5% fractional raw-quality oracle
  share;
- at least two routes each receive at least 10% fractional utility-oracle
  share;
- route top-1 paragraphs disagree on at least 20% of test queries.

### G2 — decision headroom

Against `F_dev` on official validation:

- mean utility oracle headroom at least `.060`;
- 95% lower bound above `.040`;
- mean raw NDCG oracle headroom at least `.080`.

### G3 — non-saturation and stratum breadth

- no route dominates all others in test mean NDCG and mean operator cost;
- the strongest test fixed route has NDCG below `.85`;
- at least four of the six registered hop types have utility oracle headroom
  at least `.040`.

### G4 — recoverable signal

`A_dev - F_dev` test utility:

- mean at least `.010`;
- paired-bootstrap lower bound above zero;
- recovers at least 10% of `F_dev`-to-oracle headroom.

G4 is a benchmark finding, not a proposed-method claim.

### G5 — target/control fidelity

- real V2 minus shuffled-V2 mean NDCG at least `.20`, lower bound above `.15`;
- real V3 minus wrong-decomposition V3 mean NDCG at least `.03`, lower bound
  above `.02`.

## 8. Decision

- **FULL PASS:** G0--G5 pass; MuSiQue satisfies the complete structured-family
  WorthIR task criteria.
- **RESOURCE PASS / RECOVERABILITY NEGATIVE:** G0--G3 and G5 pass but G4
  fails; the evaluation surface is valid but does not support a positive
  adaptive result.
- **BOUNDED REPAIR:** only a precise implementation/provenance defect, without
  changing membership, routes, costs, features, or thresholds.
- **FAIL:** any substantive G0--G3 or G5 failure.

No result-dependent route, threshold, feature, or sample change is permitted.

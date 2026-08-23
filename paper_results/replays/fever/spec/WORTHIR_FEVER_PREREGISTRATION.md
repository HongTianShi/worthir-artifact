# WorthIR--FEVER preregistration

Status: **frozen before retrieval outcomes**  
Version: `worthir-fever-prereg-v1.0`  
Freeze date: 2026-07-30  
Seed: `20260730`

## 1. Scientific role

WorthIR--FEVER is an orthogonal fact-verification document-retrieval task.  It
tests whether the same buy-before-score contract can evaluate a conventional
multi-stage IR pipeline over a 5.4M-page corpus, rather than another
multi-hop-support-title task.  It is a retrospective, outcome-separated
validation task; it is not described as prospective evidence.

The task asks: given a verifiable FEVER claim, which retrieval route should be
purchased before route-specific rankings or relevance outcomes are visible?
Every route returns a ranking over the same frozen Wikipedia page corpus.

## 2. Frozen population and target

- Claims: official FEVER train and shared-task development JSONL files.
- Corpus: the official 2017 FEVER Wikipedia dump.
- Included labels: `SUPPORTS` and `REFUTES`; `NOT ENOUGH INFO` is excluded
  because it has no document-retrieval target.
- Query: the claim text only.
- Relevant documents: the union of canonical Wikipedia page identifiers that
  occur in at least one complete, sentence-valid official evidence set.
- Primary metric: document `NDCG@10`, binary page relevance.
- Secondary metrics: `Recall@10` and complete-evidence-set page recall at 10.
- Unicode rule: page identifiers are mapped to the unique NFC-normalized
  corpus identifier. Ambiguous normalized identifiers fail closed.
- Index serialization rule: FEVER escape tokens for brackets and colons are
  deterministically decoded only when the resulting identifier resolves
  exactly in the frozen Lucene index. Missing, ambiguous, or many-to-one
  mappings fail closed.

Exact normalized claim strings define leakage groups.  The development
population excludes the three train claim hashes that also occur in official
development.  Pilot membership is frozen at 1,200 queries: 600 admission
train, 300 admission development, and 300 admission test, stratified by label
and single-/multi-page evidence.  The full evaluation uses 6,000 disjoint
official-train development queries and all 13,332 verifiable official
shared-task-development queries as the outcome-separated test.

## 3. Legal state

At purchase time a policy may use:

- claim text and qrel-independent lexical features;
- claim length and token counts;
- the base BM25 top-200 document identifiers, ranks, scores, and score-shape
  summaries;
- declared route descriptors and cost profiles.

It may not use:

- FEVER labels, qrels, evidence page or sentence identifiers;
- paid-route scores, rankings, quality, utility, regret, or oracle actions;
- any field derived from the official admission/full test outcomes;
- a threshold, route, or hyperparameter selected on admission/full test.

Legality is established by field lineage, not by column name.

## 4. Frozen route menu

All routes inherit one BM25 candidate-generation execution with up to 200
real matching documents,
Lucene BM25 `k1=0.9`, `b=0.4`, and the frozen Pyserini FEVER flat index.

1. `bm25`: retain the BM25 order.
2. `bi200`: rerank all 200 candidates by cosine similarity using
   `sentence-transformers/all-MiniLM-L6-v2` at revision
   `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
3. `ce20`: cross-encode and rerank the BM25 top 20 using
   `cross-encoder/ms-marco-MiniLM-L6-v2` at revision
   `c5ee24cb16019beea0893ab7796b1df96625c6b8`.
4. `ce100`: cross-encode and rerank the BM25 top 100 using the same frozen
   cross-encoder.
5. `hybrid`: rerank the available BM25 pool with the bi-encoder, then cross-encode its
   top 20.

Bi-encoder sequences are truncated by the frozen tokenizer to 256 tokens.
Cross-encoder pairs are truncated to 512 tokens.  Ties use original BM25 rank
and then document identifier.  No route may retrieve outside the common
top-200 pool in version 1.0.

Dependencies are cumulative: `bi200` includes BM25; `ce20` and `ce100` include
BM25; `hybrid` includes BM25, `bi200`, and its top-20 cross-encoder execution.

## 5. Cost and preference profiles

The headline cost is qrel-independent **operator-counted token work** beyond
the common BM25 parent.  It counts actual non-padding tokenizer tokens scored
by each paid transformer and divides by the maximum permitted work of
`hybrid` (200 bi-encoder document sequences plus 20 cross-encoder pairs).
The common BM25 parent is reported separately and has zero incremental cost
for within-menu purchase comparisons.

Measured warm latency on the registered RTX 4070 Laptop GPU is a secondary,
hardware-qualified profile.  Raw quality, operator work, latency, hard-budget
readouts, and the quality--cost frontier are retained; no scalar utility is
presented as the only evaluation.

For scalar readouts:

`U_lambda(q,v) = NDCG@10(q,v) - lambda * C(q,v)`,

with `lambda` in `{0, .02, .04, .08, .16}` and `.08` as the headline profile.
Costs and lambda are never predictor fields.

## 6. References and policy selection

- `F_dev`: one fixed route selected using admission development (pilot) or
  the 6,000-query development set (full), then frozen.
- `F_TIH`: test-in-hindsight best fixed route, diagnostic only.
- `A_dev`: a policy whose family and hyperparameters are selected without
  admission/full test outcomes and whose test actions use only legal state.
- `O_TIH`: per-query evaluator-only route oracle.

The pilot may evaluate fixed policies, a margin heuristic, and
capacity-bounded RF/ExtraTrees multi-output raw-quality predictors.  These are
measurement probes, not proposed methods.  Adaptive gain is not an admission
condition.

## 7. Pilot admission gate

All four integrity conditions must pass:

1. authoritative membership, target mapping, schema, and leakage checks pass;
2. every query-route outcome is finite and uses the registered parent pool;
3. route fingerprints, candidate closure, and cost accounting reproduce;
4. a frozen shuffled-qrel control loses at least 80% of the unshuffled best
   fixed `NDCG@10`.

Proceed to full evaluation when at least three of four scientific conditions
hold on the 300-query admission test:

1. `F_dev` test `NDCG@10 >= .15`;
2. raw oracle headroom is at least `.01`, or headline-utility oracle headroom
   is at least `.005`;
3. the second-most-common oracle route serves at least 3% of queries;
4. at least one paid route improves mean raw `NDCG@10` over BM25 by `.003`,
   or improves at least 5% of queries by `.05`.

These are task-admission checks, not hypotheses that WorthIR must reverse the
winner or make an adaptive learner positive.

## 8. Full-evaluation rule

If the pilot passes, all route definitions, metrics, costs, membership rules,
and selection semantics remain frozen.  Full evaluation runs on the frozen
6,000-query development population and 13,332-query official-development test.
Any technical amendment must be append-only, result-blind where possible, and
must not relax a scientific threshold after observing it.

## 9. Strongest permitted claims

- **Strongest defensible:** WorthIR can represent and audit a conventional
  multi-stage fact-verification retrieval pipeline when the registered task
  passes the integrity and admission gates.
- **Conservative fallback:** the task supplies a validated additional
  retrieval surface but has limited route heterogeneity or recoverable value.
- **Prohibited:** FEVER proves universal superiority of WorthIR, provides a
  prospective test, or establishes a causal or information-theoretic limit.

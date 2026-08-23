# TREC walkthrough

This is a tiny retrieval task in standard TREC formats. It demonstrates the
full human workflow without downloading data.

```bash
python worthir.py demo
```

The command computes NDCG@3 from `source/qrels.tsv` and the three TREC runs,
builds a WorthIR task, scores the supplied policy, evaluates every fixed route,
and writes `reproduced/trec_walkthrough/comparison.md`.

To try another policy after the demo:

```bash
python worthir.py actions reproduced/trec_walkthrough examples/trec_walkthrough/source/alternative_choices.csv --policy-id alternative
python worthir.py compare reproduced/trec_walkthrough
```

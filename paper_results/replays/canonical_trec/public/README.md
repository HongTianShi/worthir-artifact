# TREC-DL replay

Choose one route for every topic in a file under `public/reference_submissions/`,
then run:

```bash
python score_actions.py \
  --actions public/reference_submissions/stop_bm25.json \
  --output score.json
```

Available routes are `stop_bm25`, `dense_fusion`, `late_interaction`, and
`cross_encoder`. The output reports NDCG@10, cost, utility, and regret for
2019 and 2020 separately.

Raw qrels, full rankings, and MS MARCO development tables are not distributed.

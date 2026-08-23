# FEVER Reconstruction Card

The released scoring surface is under `replays/fever/`. It contains legal
state, frozen actions, a complete released five-route ledger, operator-work
costs, a hardware-qualified latency report, and a fail-closed scorer.

Raw reconstruction additionally requires the official FEVER 2017 Wikipedia
dump, the corresponding page index, the checkpoints used by `bi200`,
`ce20`, `ce100`, and `hybrid`, and the candidate caches. Every route must rank
the same 5,416,537-page corpus. The primary cost is actual non-padding
transformer-token work beyond the common BM25 parent; measured RTX 4070
Laptop warm latency is a secondary hardware-qualified profile.

The released action replay is:

```text
python replays/fever/scripts/score_actions.py \
  --bundle-root replays/fever \
  --actions replays/fever/frozen_results/registered_actions_lambda08.csv \
  --lambda-value 0.08 \
  --output reproduced/fever_score.json
```

This scores frozen outcomes; it does not claim to rerun the 5.4M-page
retrieval pipeline.


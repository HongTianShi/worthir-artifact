# 2Wiki-Structured evaluator ledger

This directory contains the 2,000-query, five-route outcome ledger and the
support-title-component-disjoint references bound to the public task surface.
It is evaluator input and must never be used to train or select a policy.

```bash
python score_submission.py \
  --public-root ../public \
  --private-root . \
  --submission my_policy.json \
  --output score.json
```

The scorer returns aggregate results. Uncertainty intervals resample the 1,636
support-title connected components.

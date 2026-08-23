# WorthIR Structured-v2 Public Scoring Surface

Task: `worthir-2wiki-structured-v2.0`

This package exposes 2,000 legal purchase-time query states and five declared
evidence views. It contains no query-view outcomes, qrels, support titles,
oracle actions, utility, regret, paid-view scores, or learned policy outputs.

Create exactly one action per `query_uid` using
`templates/submission_template.json`, then run:

```text
python validate_submission.py --public-root . --submission my_policy.json
```

The organizer-side scorer joins actions to a private complete outcome ledger
and returns aggregate quality, cost, utility, exact within-menu regret, action
shares, and comparisons to frozen references. The supplied adaptive reference
is explicitly `A_OOF`: every query was scored by a policy fitted without its
support-title component. An action vector alone does not certify its training
lineage; supervised fold compliance requires evaluator-run isolation.

Because the source task is public, query identifiers can be joined back to
2Wiki outside this package. The legal-state boundary is a temporal evaluation
contract, not a cryptographic confidentiality claim. A hosted evaluator should
rate-limit and batch-release scores to limit differencing attacks across
near-identical submissions.

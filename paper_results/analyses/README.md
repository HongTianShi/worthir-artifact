# RQ2–RQ5 analyses

Run from the repository root:

```bash
python scripts/reproduce_rqs.py --output-dir reproduced/rqs
```

The command validates released tables, recomputes RQ2 policy means from
per-query route outcomes and actions, and writes compact Markdown/CSV readouts.
It does not download corpora, train routers, or execute neural retrieval.

| Directory | Contents |
| --- | --- |
| `rq2_policy_comparison/` | Matched policy results, cost controls, Holm tests, and FEVER latency |
| `rq3_utility_sources/` | Query strata, predictability, and top-decile switching |
| `rq4_robustness/` | Cost-preference, recurrence, learner, and fold checks |
| `rq5_route_value/` | Relevant-page depth, graph/decomposition controls, and route-value prediction |

`structured_v2` is the stable machine-readable identifier for
2Wiki-Structured. RQ3–RQ5 are post-outcome diagnostics and should not be
interpreted as prospective policy evaluations.

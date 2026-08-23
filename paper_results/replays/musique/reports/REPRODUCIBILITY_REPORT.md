# MuSiQue-WorthIR reproducibility report

**Result: PASS.**

The frozen materializer was executed from a new empty output directory. Full route rankings, query-route metrics, controls, purchase-time policy state, candidate-pool fingerprints, and execution semantics were compared to the canonical bundle.

| Object | Result |
|---|---:|
| `route_outcomes_private.parquet` | PASS |
| `controls_private.parquet` | PASS |
| `policy_state.parquet` | PASS |
| `candidate_pool_fingerprints.parquet` | PASS |
| `query_index.parquet` | PASS |
| `rankings_private.npz` | PASS |
| `execution_manifest_semantics` | PASS |

`route_runtime.parquet` is excluded because wall-clock latency is a non-headline machine diagnostic. The frozen operator-counted cost and every scientific outcome are included in the exact comparison.

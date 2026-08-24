# Bring your own router

Run the complete example from the repository root:

```powershell
.\worthir.cmd demo-custom
```

```bash
./worthir demo-custom
```

The example builds a non-TREC task, runs `router.py`, binds its CSV decisions to
the task contract, and compares the router with every fixed route. The report is
written to `reproduced/custom_task/comparison.md`.

`router.py` reads the public task contract, route registry, lambda,
`participant/legal_state.csv`, and `participant/route_costs.csv`. It selects the
route with the highest predicted effectiveness minus lambda times public cost.
It never opens `evaluator/ledger.csv`, which contains information unavailable
when a route is selected. To use your own router, replace
`predicted_effectiveness()` and keep the two-column output format:

```text
query_uid,selected_route_id
```

For an existing task, evaluate that CSV in one command:

```powershell
.\worthir.cmd evaluate TASK choices.csv --policy-id my-router
```

```bash
./worthir evaluate TASK choices.csv --policy-id my-router
```

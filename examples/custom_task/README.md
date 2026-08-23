# Custom task input

This example is not a TREC ranking task. Its effectiveness measure is
`answer_coverage`, and its execution cost varies by query.

The four source files are the complete generic adapter interface:

- `task.json` names the effectiveness measure and cost profile.
- `queries.csv` contains only information a router may use.
- `routes.csv` defines available routes, prerequisites, and route costs.
- `outcomes.csv` contains evaluator-only effectiveness and cost outcomes for
  every query--route pair.

Build and validate it from the repository root:

```powershell
.\worthir.cmd build-custom examples/custom_task/source reproduced/custom_task
.\worthir.cmd validate-task reproduced/custom_task
```

```bash
./worthir build-custom examples/custom_task/source reproduced/custom_task
./worthir validate-task reproduced/custom_task
```

Use `cost` when cumulative route costs are already available. Use
`incremental_cost` when the tool should sum the transitive prerequisite closure.
Either column may appear in `outcomes.csv` to provide query-dependent values.
Set `cost_profile.availability` to `known_at_commitment` when the router may use
the cost before choosing a route. The builder then publishes fixed costs in the
route registry or query-dependent costs in `participant/route_costs.csv`. Use
`measured_after_execution` when cost is evaluator-only.

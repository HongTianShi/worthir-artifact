# Apply WorthIR to a new task

Run commands from the repository root. Use the generic adapter unless your data
already consists of qrels and TREC run files.

## Generic task

Create one source directory:

```text
my_source/
  task.json
  queries.csv
  routes.csv
  outcomes.csv
  policy_choices.csv       optional
```

### 1. Name the measure and cost profile

`task.json` declares a higher-is-better effectiveness measure and the cost
preference used in `utility = effectiveness - lambda * cost`:

```json
{
  "task_id": "my-task-v1",
  "metric": {
    "name": "answer_coverage",
    "minimum": 0.0,
    "maximum": 1.0,
    "higher_is_better": true
  },
  "cost_profile": {
    "profile_id": "latency-seconds-v1",
    "provenance": "expected execution time estimated on an independent calibration set",
    "lambda": 0.15,
    "availability": "known_at_commitment"
  },
  "development_selected_fixed_route": "standard"
}
```

The measure need not be NDCG or a TREC measure. WorthIR consumes the numerical
outcome supplied for each query and route.

### 2. Separate router input from evaluator outcomes

`queries.csv` contains only fields available when the router chooses a route.
Its first column must be `query_uid`:

```csv
query_uid,question_length,domain
q1,12,sports
q2,31,science
```

`outcomes.csv` is evaluator-only and must contain every query--route pair:

```csv
query_uid,route_id,effectiveness
q1,standard,0.81
q1,extended,0.89
q2,standard,0.64
q2,extended,0.91
```

Do not use this file to train or execute a held-out router unless the task's
data split explicitly makes those rows development data.

### 3. Define routes and costs

Prerequisites are semicolon-separated route IDs. Exactly one route is the fixed
reference selected on development data.

If cumulative costs are already known:

```csv
route_id,label,prerequisites,cost,development_selected
standard,Standard route,,0.10,true
extended,Extended route,standard,0.40,false
```

If routes are components in a dependency graph, use `incremental_cost` instead:

```csv
route_id,label,prerequisites,incremental_cost,development_selected
lexical,Lexical search,,0.03,false
semantic,Semantic search,,0.12,true
combined,Combined review,lexical;semantic,0.08,false
```

WorthIR sums each route's transitive prerequisite closure once. To make costs
query-dependent, add the same `cost` or `incremental_cost` column to
`outcomes.csv` and provide a value for every pair. Do not mix the two cost modes.
When availability is `known_at_commitment`, the builder publishes fixed costs
in `contracts/route_registry.json` or query-dependent cumulative costs in
`participant/route_costs.csv`. Use `measured_after_execution` when the router
cannot know the cost until a route has run; those costs stay evaluator-only.

### 4. Build and validate

```powershell
.\worthir.cmd build-custom my_source my_task
.\worthir.cmd validate-task my_task
```

```bash
./worthir build-custom my_source my_task
./worthir validate-task my_task
```

Validation reports query and route counts, missing combinations, dependency
problems, cumulative-cost violations, when costs become available, and whether
every public cost matches the evaluator ledger.

### 5. Run a router and compare it

The router reads the task contract, public route registry,
`my_task/participant/legal_state.csv`, and any public costs. It writes:

```csv
query_uid,selected_route_id
q1,standard
q2,extended
```

Bind and compare those decisions in one command:

```powershell
.\worthir.cmd evaluate my_task choices.csv --policy-id my-router
```

See [`examples/custom_router/`](../examples/custom_router/) for a complete
router that never reads the evaluator ledger.

## TREC adapter

For qrels and six-column TREC runs, follow
[`examples/trec_walkthrough/`](../examples/trec_walkthrough/). Its `routes.csv`
adds a `run_file` column, and `build-trec` computes NDCG@K before creating the
same task structure:

```powershell
.\worthir.cmd build-trec my_source my_task --task-id my-task-v1 --metric ndcg@10 --lambda 0.08
.\worthir.cmd validate-task my_task
```

The optional TREC `costs.csv` supplies cumulative query-dependent costs with
columns `query_uid,route_id,cost`. Add `--cost-availability
measured_after_execution` only when those costs were not known when the route
was selected.

## Outputs

`compare` and `evaluate` write a readable `comparison.md`, machine-readable
CSV and JSON, and `fixed_routes.csv` with Pareto membership. These are
descriptive query means. Statistical intervals require a task-appropriate
resampling design; the generic tool does not invent one.

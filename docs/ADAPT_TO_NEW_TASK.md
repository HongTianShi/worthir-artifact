# Apply WorthIR to a retrieval task

The shortest path starts from standard qrels and TREC run files. Run every
command from the repository root.

## 1. Create the source folder

```text
my_source/
  qrels.tsv
  routes.csv
  queries.csv              optional
  costs.csv                optional
  policy_choices.csv       optional
  runs/
    base.trec
    advanced.trec
```

`qrels.tsv` accepts the usual four-column TREC form:

```text
query_id 0 document_id relevance
```

Three-column `query_id document_id relevance` rows are also accepted.

Each run is a six-column TREC run:

```text
query_id Q0 document_id rank score run_name
```

`routes.csv` has exactly these columns:

```csv
route_id,label,parent_route_id,run_file,cost,development_selected
base,BM25,,runs/base.trec,0.00,false
advanced,Cross-encoder,base,runs/advanced.trec,0.75,true
```

Exactly one route must be marked `development_selected`. This is the strong
fixed reference selected without using evaluation outcomes. `parent_route_id`
records required preceding work. Costs are cumulative: a child route cannot
cost less than its parent.

If every query has the same route cost, the `cost` column is enough. For
measured query-dependent latency or work, add `costs.csv` with one row for every
query--route pair:

```csv
query_uid,route_id,cost
q1,base,12.4
q1,advanced,48.7
```

When present, `costs.csv` replaces the constant route costs. See
[`COST_AND_LAMBDA.md`](COST_AND_LAMBDA.md) before choosing the scale and lambda.

`queries.csv` is participant-visible state. Its first column must be
`query_uid`, and it must contain each qrels query once. Put only information
available before route selection in this file. If it is omitted, WorthIR writes
a one-column query list.

`policy_choices.csv` is optional and has two columns:

```csv
query_uid,selected_route_id
q1,base
q2,advanced
```

If it is absent, the generated default policy selects the development-selected
fixed route for every query. If it is present, give the policy a meaningful
name with `--policy-id` when building the task.

## 2. Build and inspect the task

```powershell
.\worthir.cmd build-trec my_source my_task --task-id my-retrieval-task-v1 --metric ndcg@10 --lambda 0.08 --policy-id my-router
```

Use `./worthir` on macOS or Linux. The built task contains:

```text
my_task/
  contracts/task_contract.json
  contracts/route_registry.json
  participant/legal_state.csv
  participant/actions.json
  participant/policies/
  evaluator/ledger.csv
```

The adapter computes NDCG@K for every qrels query and every registered run.
Inspect a few ledger rows before proceeding. Relevance judgments and the ledger
are evaluator-side data; a routing policy must not use them.

## 3. Add routing policies

Export each policy's held-out choices as a CSV containing `query_uid` and
`selected_route_id`, then bind it to the task:

```powershell
.\worthir.cmd actions my_task choices.csv --policy-id my-router
```

The resulting JSON is written to `my_task/participant/policies/my-router.json`.
The command rejects missing queries, duplicates, and unknown routes.

## 4. Compare policies

```powershell
.\worthir.cmd compare my_task
```

This scores the default action file, every JSON file in
`participant/policies/`, and every registered fixed route. It writes:

- `comparison.md`: readable task summary;
- `comparison.csv`: policy and fixed-route means;
- `fixed_routes.csv`: fixed-route points and Pareto membership;
- `comparison.json`: complete machine-readable output.

See [`OUTPUTS.md`](OUTPUTS.md) for interpretation. These files contain
descriptive query means. Statistical intervals require a task-appropriate
resampling design and are not invented by the generic tool.

## Manual route

For non-TREC effectiveness measures, create an editable task and replace the
example ledger with one complete query--route matrix:

```powershell
.\worthir.cmd init my_task --task-id my-task-v1
.\worthir.cmd score my_task
```

The ledger columns are `query_uid,route_id,effectiveness,cost`. Effectiveness
must be higher-is-better and lie within the bounds in the task contract.

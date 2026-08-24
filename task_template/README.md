# Editable task template

`worthir init` copies this runnable one-query task. Replace the example routes,
participant-visible state, actions, and complete evaluator ledger, then run
`worthir compare TASK_DIR` from the repository root.

The template uses fixed costs known at commitment time, so the same cumulative
cost appears on each route in `contracts/route_registry.json` and in the
evaluator ledger. `validate-task` rejects any disagreement.

The contract also declares example lambda and hard-budget grids. After actions
are frozen, `worthir analyze`, `worthir sensitivity`, `worthir budget`, and
`worthir plot` write evaluator-only diagnostics under `organizer_private/`.

For most tasks, `worthir build-custom` is faster and less error prone than
editing this template manually. Standard qrels and TREC runs can use
`worthir build-trec`.

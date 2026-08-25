# CLI command reference

Most users should call `worthir` after installing from PyPI, or use
`worthir.cmd`/`./worthir` from a source checkout. The files below implement
those public commands.

- `build_trec_task.py`: convert qrels, TREC runs, and costs into a task.
- `build_custom_task.py`: build a task from generic query, route, outcome, and cost tables.
- `validate_task.py`: check the complete task before any policy is scored.
- `actions_from_csv.py`: bind a query--route choice CSV to a task.
- `compare_policies.py`: score policies and fixed routes and write reports.
- `score_actions.py`: score one action file.
- `analyze_task.py`: write organizer-only per-query diagnostics.
- `sensitivity.py`: evaluate frozen actions across a lambda grid.
- `budget.py`: summarize hard per-query cost ceilings.
- `plot_pareto.py`: draw a dependency-free descriptive Pareto SVG.
- `init_task.py`: copy the editable task template.
- `run_smoke_test.py`, `run_integrity_tests.py`, and `validate_framework.py`:
  framework checks used by `worthir doctor`.

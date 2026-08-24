# `worthir_eval` Package

This package implements the compact WorthIR evaluation interface.

- `core.py` loads contracts and action vectors, validates route dependencies and
  cumulative costs, joins evaluator-only outcomes, and computes effectiveness,
  cost, utility, and regret summaries.
- `analysis.py` computes explicitly organizer-only per-query diagnostics,
  lambda sensitivity, hard-budget summaries, and fixed-route Pareto points.
- `__init__.py` exposes the supported public symbols.

`inspect_task()` validates and summarizes a task before scoring.
`load_and_score()` scores one contract-bound action file.
`per_query_analysis()`, `sensitivity_analysis()`, `budget_analysis()`, and
`fixed_route_points()` require evaluator data and must not feed router inputs.

The package preserves the participant/evaluator boundary: participant-visible
inputs are sufficient to form actions, while complete route outcomes are
joined only during evaluation.

# `worthir_eval` Package

This package implements the compact WorthIR evaluation interface.

- `core.py` loads contracts and action vectors, validates route selections, joins evaluator-only outcomes, and computes effectiveness, cost, utility, and regret summaries.
- `__init__.py` exposes the supported public symbols.

The package preserves the participant/evaluator boundary: participant-visible
inputs are sufficient to form actions, while complete route outcomes are
joined only during evaluation.

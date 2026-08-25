# Contributing

Contributions should make a task easier to define, a router easier to evaluate,
or a released result easier to verify. Bug fixes, clearer task adapters, and
small runnable examples are welcome.

Before opening a pull request:

```bash
python scripts/validate_framework.py
python paper_results/run.py
```

For a new task, include a small licensed or synthetic example under
`examples/`, document the effectiveness measure and cost provenance, and make
the information available to the router explicit. Evaluator outcomes must not
appear in participant inputs. Run `worthir validate-task` on the generated task
and include the exact command in its README.

Do not commit downloaded corpora, model checkpoints, indexes, local virtual
environments, or generated task outputs. Keep pull requests focused on what a
reader needs to run or understand the change.

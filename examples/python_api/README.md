# Python API

After building any WorthIR task, inspect and score it without the CLI:

```bash
python examples/python_api/example.py reproduced/custom_task
```

`inspect_task` validates the task contract, public information, route
dependencies, and complete evaluator ledger. `load_and_score` then joins a
contract-bound action file with the hidden ledger and returns aggregate
effectiveness, cost, utility, regret, and route counts.

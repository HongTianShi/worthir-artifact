#!/usr/bin/env python3
"""Inspect and score one WorthIR task through the Python API."""

import json
import sys
from pathlib import Path

from worthir_eval import inspect_task, load_and_score

task = Path(sys.argv[1])
contract = task / "contracts" / "task_contract.json"
ledger = task / "evaluator" / "ledger.csv"
actions = task / "participant" / "actions.json"
state = task / "participant" / "legal_state.csv"

print(json.dumps(inspect_task(contract, ledger, state), indent=2))
print(json.dumps(load_and_score(contract, ledger, actions), indent=2))

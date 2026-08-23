# Figure builders

- `make_worthir_contract.py`: protocol overview.
- `make_cost_quality_inversion.py`: fixed-route cost/effectiveness profile.
- `make_recoverability_bridge.py`: within-task recoverability figure.

The adjacent CSV/JSON files are the compact inputs used by these scripts. Run
all builders through `python scripts/reproduce_paper.py --output-dir
reproduced/paper` so input and arithmetic checks are applied first.

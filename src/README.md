# Python Package Source

This directory contains the dependency-free evaluator used by the public commands.
`setup_environment.py` exposes it in the local environment through a `.pth`
file, so no package build or network installation is required.

`worthir_eval/` contains the public scoring API, organizer-only analysis API,
and core validation logic.
Command-line entry points are under `../scripts/`.

Keep task-specific data assumptions out of the generic package.

# Paper results

This directory contains the data and code used to reproduce the results in
the WorthIR paper.

From this directory, run:

```bash
python run.py
```

The command creates a local environment, reproduces the paper figures and
tables, rebuilds the RQ2--RQ5 summaries, and validates the released task
ledgers. It keeps all outputs instead of discarding them:

- `reproduced/paper/`: rebuilt paper figures, tables, and manifests.
- `reproduced/rqs/`: rebuilt RQ2--RQ5 summaries.
- `reproduced/validation.json`: validation steps and exit status.

See [`PAPER_MAP.md`](PAPER_MAP.md) for the exact relationship between paper
items, repository inputs, commands, and outputs.

The main contents are:

- `analyses/`: RQ2--RQ5 result tables and action files.
- `replays/`: released task ledgers and task-specific scorers.
- `paper_reproduction/`: figure and table inputs and builders.
- `full_replay/`: requirements for rebuilding retrieval outputs.
- `docs/`: reference semantics, data sources, and third-party terms.

Large corpora, indexes, model weights, and raw rankings are not included.

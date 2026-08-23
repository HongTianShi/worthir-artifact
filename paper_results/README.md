# Paper results

This directory contains the data and code used to reproduce the results in
the WorthIR paper.

From this directory, run:

```bash
python run.py
```

The command creates a local environment, reproduces the paper figures and
tables, rebuilds the RQ2--RQ5 summaries, and validates the released task
ledgers.

The main contents are:

- `analyses/`: RQ2--RQ5 result tables and action files.
- `replays/`: released task ledgers and task-specific scorers.
- `paper_reproduction/`: figure and table inputs and builders.
- `full_replay/`: requirements for rebuilding retrieval outputs.
- `docs/`: reference semantics, data sources, and third-party terms.

Large corpora, indexes, model weights, and raw rankings are not included.

# Rebuild the original retrieval routes

This workflow starts before the released WorthIR ledgers. It checks separately
obtained corpora and checkpoints, runs a task adapter, converts its complete
query--route outcomes into a WorthIR ledger, and validates the result. Those
external materials are not redistributed here. FiQA-Compression260 needs no
manually prepared index: its task adapter downloads the public corpus and
models and builds the required representations locally.

For the runnable FiQA reconstruction:

```bash
python -m pip install -r paper_results/full_replay/fiqa260/requirements.txt
python paper_results/full_replay/replay.py fiqa260 prepare --workspace replay-work/fiqa260
python paper_results/full_replay/replay.py fiqa260 smoke --workspace replay-work/fiqa260
```

See [`FIQA260.md`](FIQA260.md) for the complete 260-query run.

Choose a task and an empty workspace:

```bash
python paper_results/full_replay/replay.py fever prepare \
  --workspace replay-work/fever \
  --input wikipedia=/data/fever/wiki-pages \
  --input index=/data/fever/lucene-index \
  --input checkpoints=/models/fever \
  --input candidate_cache=/data/fever/bm25-candidates
```

`prepare` writes `replay.json`, reports any missing material, copies a small
route-adapter template, and prints the hardware estimate. Replace the template
with the registered route runner described in the task guide, or make the two
command arrays in `replay.json` call an existing runner. The adapter writes
`task.json`, `queries.csv`, `routes.csv`, and `outcomes.csv` to its `--output`
directory.

Run the same five stages for every task:

```bash
python paper_results/full_replay/replay.py fever prepare --workspace replay-work/fever
python paper_results/full_replay/replay.py fever smoke --workspace replay-work/fever
python paper_results/full_replay/replay.py fever run-routes --workspace replay-work/fever
python paper_results/full_replay/replay.py fever build-ledger --workspace replay-work/fever
python paper_results/full_replay/replay.py fever verify --workspace replay-work/fever
```

- `prepare` checks paths and records them locally.
- `smoke` asks the adapter to run 20 queries.
- `run-routes` runs the full configured adapter.
- `build-ledger` uses the public generic-task builder.
- `verify` checks the WorthIR contract and the registered query/route counts.

The final numerical check against the released paper results remains:

```bash
python paper_results/run.py
```

This separation is intentional: a reconstructed route run may differ slightly
with hardware or upstream model versions, while the released-ledger workflow
must close exactly. Read [`RESOURCE_REQUIREMENTS.md`](RESOURCE_REQUIREMENTS.md)
before downloading data, then use the task guide:

- [`CANONICAL_TREC.md`](CANONICAL_TREC.md)
- [`FEVER.md`](FEVER.md)
- [`FIQA260.md`](FIQA260.md)
- [`MUSIQUE.md`](MUSIQUE.md)
- [`STRUCTURED_AND_DIAGNOSTIC.md`](STRUCTURED_AND_DIAGNOSTIC.md)

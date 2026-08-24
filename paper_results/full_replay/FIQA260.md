# Rebuild FiQA-Compression260

This replay rebuilds the eight FiQA routes used in the paper from the official
BEIR FiQA corpus. It downloads the corpus and the two registered public models,
encodes all 57,638 documents, runs the fixed 260-query set, and writes a WorthIR
ledger. No manually prepared index is required.

The routes are summary retrieval, binary dense retrieval, IVF--PQ, 96- and
192-dimensional truncation, int8 dense retrieval, full dense retrieval, and
cross-encoder reranking of the full-dense top 50. Their registered operator
costs are written to the public route registry before policy selection.

## Set up

Use a Python 3.10--3.13 environment. For a CPU machine, run the bundled
installer. It obtains PyTorch from the official CPU wheel index before
installing the remaining fixed dependencies, avoiding the CUDA runtime packages
carried by the default Linux wheel:

```bash
python paper_results/full_replay/fiqa260/install_cpu.py
```

If the machine has a supported CUDA or ROCm accelerator, install the matching
PyTorch build using the official PyTorch selector, then run
`python -m pip install -r paper_results/full_replay/fiqa260/requirements.txt`.

Prepare a workspace. The command records the bundled adapter automatically:

```bash
python paper_results/full_replay/replay.py fiqa260 prepare --workspace replay-work/fiqa260
```

## Run

The smoke test evaluates 20 registered queries. The first run also downloads
the corpus and models and creates the reusable document embeddings and indexes.
On a CPU-only Windows workstation, this one-time setup took about ten minutes;
the first complete 260-query cross-encoder stage took about three minutes.
Once both caches existed, the complete route run took about 22 seconds.
Hardware and model-cache state will change those times.

```bash
python paper_results/full_replay/replay.py fiqa260 smoke --workspace replay-work/fiqa260
```

Reuse the cache for the complete 260-query run, build the evaluator ledger, and
validate its contract:

```bash
python paper_results/full_replay/replay.py fiqa260 run-routes --workspace replay-work/fiqa260
python paper_results/full_replay/replay.py fiqa260 build-ledger --workspace replay-work/fiqa260
python paper_results/full_replay/replay.py fiqa260 verify --workspace replay-work/fiqa260
```

The primary outputs are:

- `replay-work/fiqa260/task/evaluator/ledger.csv`: all 2,080 query--route outcomes;
- `replay-work/fiqa260/task/participant/legal_state.csv`: router-visible query state;
- `replay-work/fiqa260/task/contracts/route_registry.json`: routes, prerequisites,
  and public costs;
- `replay-work/fiqa260/fiqa260_rebuild_summary.json`: rebuilt route means beside
  the paper values.

The official FiQA archive is checked against its registered SHA256 before
extraction. Model files use their registered Hugging Face revisions. The
adapter keeps the downloaded corpus, embeddings, summary index, and IVF--PQ
index under the replay workspace so subsequent stages do not repeat them.

The two truncated routes, int8 route, full dense route, and cross-encoder route
are deterministic and are checked against the paper means. Summary retrieval,
binary retrieval, and IVF--PQ depend on FAISS clustering, approximate search, or
the ordering of tied binary scores. Their rebuilt means are reported beside the
paper values rather than silently replaced by frozen outcomes.

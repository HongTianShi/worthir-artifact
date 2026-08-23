# Raw-route reconstruction requirements

The default `python run.py` path uses compact released ledgers. Raw retrieval
reconstruction requires additional corpora, indexes, checkpoints, storage, and
task-specific execution time.

| Surface | External material | Main work | Expected resources |
| --- | --- | --- | --- |
| TREC-DL | MS MARCO passages/development records, TREC qrels, indexes, checkpoints | Lexical, dense, CE, and late-interaction rankings | GPU recommended; index storage dominates setup |
| FEVER | Wikipedia dump, Lucene index, checkpoints, candidate cache | Five routes over 5.4M pages | Multi-hour GPU run and large local storage |
| 2Wiki/Hyperlink10k | Candidate text and corpus-derived evidence | Route ledgers and grouped/split actions | CPU feasible after evidence materialization |
| MuSiQue | `bdsaglam/musique` and fitted policy inputs | Paragraph evidence, policy fit, validation scoring | Moderate CPU/RAM |
| FiQA260 | Source snapshot, encoders, and indexes | Compression and reranking outcomes | GPU recommended for neural routes |
| Dense-standard | Five-dataset inputs and encoders | Split ledgers | Dataset-specific |

Exact time depends on hardware, batching, and cache state. Each task card
defines its route order, costs, and source requirements. Upstream licenses
remain controlling.

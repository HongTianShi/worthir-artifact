# Task replays

Each task instantiates the same one-shot action contract while retaining its
own effectiveness measure, route set, cost definition, and evidence status.

| Surface | Entry point | Evidence type |
| --- | --- | --- |
| TREC-DL | `canonical_trec/README.md` | Retrospective task |
| FEVER | `fever/README.md` | Retrospective task |
| 2Wiki-Structured | `structured_v2/README.md` | Grouped OOF task |
| Hyperlink10k | `hyperlink10k/README.md` | Dependent stress test |
| MuSiQue | `musique/README.md` | Official-split task |
| FiQA260 | `fiqa260/README.md` | Public-label diagnostic |
| Dense-standard | `dense_and_legacy_recoverability/README.md` | Diagnostic replay |

Some directories retain the path name `organizer_private`. It means that the
contents were evaluator-only when actions were selected; released ledgers must
still never be used as policy inputs.

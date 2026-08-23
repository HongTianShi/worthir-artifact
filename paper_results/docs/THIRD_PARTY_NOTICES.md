# Third-Party Data and Model Notices

The repository-level MIT license covers WorthIR-authored code and
documentation only. It does not relicense third-party datasets, judgments,
queries, model checkpoints, or records derived from them.

| Resource | Included fields or records | Source and controlling terms | Transformation |
| --- | --- | --- | --- |
| MS MARCO / TREC Deep Learning 2019--2020 | Official topic IDs, query text, BM25 document IDs and scores, query statistics, frozen actions, and per-route metrics for 97 topics | [MS MARCO datasets and terms](https://microsoft.github.io/msmarco/Datasets.html); [TREC DL data](https://trec.nist.gov/data/deep.html). MS MARCO limits the dataset to non-commercial research. | Query statistics, rankings fingerprints, route costs, and effectiveness/utility records were added. Passage text, raw qrels, and full rankings are excluded. |
| FEVER | Official development claims, normalized claims, labels, evidence-set counts, routing-time features, actions, and per-route evidence-page metrics for 13,332 claims | [FEVER dataset](https://fever.ai/dataset/fever.html) and [FEVER data-license notice](https://fever.ai/download/fever/license.html). The annotations incorporate Wikipedia material and remain subject to the applicable Wikipedia terms or CC BY-SA 3.0. | Claims were normalized; retrieval features, route costs, actions, and document-retrieval outcomes were added. The Wikipedia corpus, index, and checkpoints are excluded. |
| 2WikiMultiHopQA | Questions, support-title identifiers in evaluator records, routing-time features, grouped actions, and per-route support-title metrics | [2WikiMultiHopQA repository](https://github.com/Alab-NII/2wikimultihop), Copyright 2020 Xanh Ho, Apache License 2.0; a copy is in `third_party/2WikiMultiHopQA-LICENSE.txt`. | Questions were assigned task IDs and folds; graph/context features, costs, actions, and retrieval outcomes were added. Source corpus materialization and the hyperlink corpus are excluded. |
| MuSiQue | Questions, decomposition questions, paragraph titles, support-title/answer fields in evaluator records, routing-time features, actions, and per-route metrics | [MuSiQue repository](https://github.com/stonybrooknlp/musique), Trivedi et al., licensed under CC BY 4.0 for the released data. | Official records were assigned task IDs; route features, costs, actions, and retrieval outcomes were added. Paragraph text and fitted models are excluded. |
| BEIR / FiQA | Query/document identifiers, diagnostic route metrics, costs, and integrity fingerprints | [BEIR repository and data guidance](https://github.com/beir-cellar/beir); upstream FiQA terms remain controlling. | Compact cost--quality diagnostic ledgers were derived; the upstream corpus and checkpoints are excluded. |

The included data records support non-commercial scientific evaluation and replay.
Users must follow each upstream license or access condition when reusing or
redistributing them. The root MIT license grants no additional data rights.

Named neural models are referenced by public checkpoint identifier in the
reconstruction documentation. Model weights are not distributed here and
remain subject to their model cards and upstream licenses.

# Data and Model Terms

WorthIR-authored source code and documentation are released under the root MIT
license. Third-party data fields and derived records keep their upstream terms;
they are not relicensed by this repository.

- **MS MARCO/TREC-DL:** the release retains the 97 official evaluation topics,
  routing-time BM25 summaries, actions, and route outcomes. MS MARCO's
  non-commercial-research condition and TREC's applicable access conditions
  remain controlling. Passages, qrels, and full rankings are omitted.
- **FEVER:** the release includes official claims and labels because they bind
  the 13,332-query evaluation ledger. FEVER's published data-license notice,
  including applicable Wikipedia or CC BY-SA terms, remains controlling. The
  Wikipedia snapshot and checkpoints are omitted.
- **2WikiMultiHopQA:** included question/support-derived records are modified
  research records from the Apache-2.0-licensed upstream release. The task is
  displayed as 2Wiki-Structured; `structured_v2` remains the stable
  machine-readable task ID.
- **MuSiQue:** included question, decomposition, title, answer, and
  support-derived records are modified research records from the CC BY 4.0
  upstream release and are attributed in `THIRD_PARTY_NOTICES.md`.
- **BEIR/FiQA and model checkpoints:** only compact diagnostic results or model
  identifiers are included. Obtain corpora and weights from their official
  sources under the applicable terms.

No credential, API token, licensed vendor export, or private cloud object is
part of this artifact.

# Data Access and Redistribution Notice

This package combines WorthIR-authored code with compact records
derived from MS MARCO and the TREC Deep Learning tracks. It does not grant
rights in the underlying data.

- MS MARCO downloads require acceptance of Microsoft's dataset terms:
  <https://microsoft.github.io/msmarco/>.
- TREC Deep Learning data and judgments remain subject to NIST's access
  conditions: <https://trec.nist.gov/data/deep.html> and
  <https://trec.nist.gov/howto.html>.

To avoid redistributing source material whose terms require separate access,
the repository excludes:

- all three `data/development/*.parquet` tables from the internal
  reconstruction package;
- raw TREC qrels;
- compressed per-route rankings and their detailed candidate audit tables.

The release retains the 2019/2020 topic legal-state tables, query membership,
frozen actions, and compact derived query--route outcomes required to score
the registered retrospective task and reproduce the reported results. The omitted
development and raw-audit files remain outside this repository. Acquisition
and rematerialization requirements are
described under `full_replay/`.

The repository-level MIT license applies only to WorthIR-authored code and
documentation. It does not relicense MS MARCO or TREC material.

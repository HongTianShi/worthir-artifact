# Raw-route reconstruction requirements

These are planning ranges, not benchmark claims. Time varies with hardware,
batching, index availability, and cache state. Disk estimates include a working
copy of indexes and intermediate route outputs.

| Task | External material | Disk | RAM | VRAM | 20-query smoke | Full route run |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| TREC-DL | MS MARCO, topics/qrels, indexes, checkpoints | 80--140 GB | 32 GB | 12 GB recommended | 20--60 min | 12--48 GPU-hours |
| FEVER | 2017 Wikipedia dump, Lucene index, checkpoints, candidates | 120--220 GB | 32 GB | 12 GB recommended | 20--60 min | 10--30 GPU-hours |
| 2Wiki/Hyperlink10k | dataset snapshot, evidence text, checkpoints | 10--30 GB | 16 GB | 8 GB recommended | 10--30 min | 1--6 GPU-hours |
| MuSiQue | dataset snapshot, paragraph evidence, checkpoints | 10--20 GB | 16 GB | 8 GB recommended | 10--30 min | 1--4 GPU-hours |
| FiQA-Compression260 | downloaded automatically | about 0.2 GB task cache plus model cache | 8 GB | not required | about 10--15 min on first CPU run | about 3 min first; 20--60 s cached |
| Dense-standard | five dataset snapshots, dense indexes, encoders | 50--150 GB | 32 GB | 12 GB recommended | 15--45 min | 4--18 GPU-hours |

The normal `python paper_results/run.py` path needs none of these external
materials. Upstream dataset and model licenses remain controlling.

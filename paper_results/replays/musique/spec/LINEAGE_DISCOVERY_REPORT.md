# MuSiQue data split

The source is the Hugging Face export `bdsaglam/musique`. Reconstruction
instructions resolve it outside this artifact.

The active retrieval unit is one answerable question:

- 19,938 training-source questions;
- 2,417 official-validation questions;
- no overlap between the two groups.

The training-source questions are divided into 15,950 training and 3,988
development examples. All 2,417 answerable official-validation questions form
the test partition.

For each query, the candidate universe is its local paragraph list, identified
by `paragraphs.idx`. Relevance is defined by the source `is_supporting`
field, and the primary measure is NDCG@4 over paragraph IDs. Paragraph IDs are
used because different passages may share a normalized title.

Development data select the fixed and learned references. The official
validation partition is used only for the final evaluation.

# MuSiQue raw reconstruction

The compact package under `replays/musique/` is sufficient for action scoring
and aggregate result reproduction.

Raw reconstruction uses `bdsaglam/musique`. Recreate paragraph evidence from
source paragraph IDs, apply the defined train/development split, fit the policy
only on those partitions, fix official-validation actions, and then join
validation outcomes. The omitted fitted model is about 342 MB; the duplicate
paragraph-evidence cache is about 137 MB.

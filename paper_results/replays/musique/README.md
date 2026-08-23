# MuSiQue replay

This package scores one selected route for each of 2,417 answerable official
validation queries.

`participant/official_validation_action_template.csv` contains `query_uid` and
`selected_route`. Valid routes are V0–V3. Outcome ledgers are evaluator inputs
under `organizer_private/`.

```bash
python scripts/score_action_file.py \
  --root . \
  --actions participant/official_validation_action_template.csv \
  --output score.json \
  --cost-profile relative_v1 \
  --lambda-value 0.08
```

Use `common_devmean_v1` for the development-normalized token-work profile.
Neither profile is physical latency, money, energy, or annotation cost.

Raw paragraph reconstruction requires the upstream MuSiQue dataset. Model
weights and duplicate paragraph caches are not included.

# Reference and Interval Semantics

WorthIR separates deployable choices from evaluator-only references. The
labels below denote information sets, not increasingly strong algorithms.

| Label | Meaning | Deployment status |
| --- | --- | --- |
| `F_dev` | One fixed route selected on development data and then frozen | Deployable for the registered evaluation |
| `A_dev` | An adaptive family and hyperparameters selected on development data, then frozen before evaluation outcomes are joined | Deployable for the registered evaluation |
| `A_OOF` | One action per query stitched from a model selected without that query or its registered group | Valid grouped cross-fitted estimate |
| `F_OOF-dev` | Foldwise fixed route selected on the fold's development partition | Valid grouped fixed reference |
| `F_OOF-TIH` | Foldwise fixed route selected after observing that fold's test outcomes | Evaluator-only diagnostic |
| `F_TIH` | One fixed route selected after observing all test outcomes | Evaluator-only diagnostic |
| `O_TIH` | Best registered route selected separately for every test query | Evaluator-only within-menu oracle |

Recovered headroom is

```text
kappa_ref = [U(A) - U(F_ref)] / [U(O_TIH) - U(F_ref)]
```

when the denominator is positive. It is the empirical fraction recovered by
the tested valid procedure within a released state and menu. It is not a
Bayes or information-theoretic limit.

## Surface-specific interpretation

| Surface | Fixed reference | Adaptive readout | Oracle | Information boundary |
| --- | --- | --- | --- | --- |
| Canonical TREC-DL | Development-selected CE | Frozen legal baselines; the tested policies retain the fixed action | `O_TIH` | Public historical topics; actions frozen before compact outcomes join |
| FEVER | `F_dev`; here equal to `F_TIH` | `A_dev`, trained and selected on official-training development claims | `O_TIH` | Actions validated before the official shared-development evidence join |
| Structured-v2 | `F_OOF-dev` and `F_OOF-TIH` | `A_OOF` over support-title components | `O_TIH` | Every query action comes from a fold that excludes its registered component |
| MuSiQue | `F_dev`; here equal to `F_TIH` | Workflow-frozen `A_dev` on official validation | `O_TIH` | Train/development selection frozen before official-validation scoring |
| Hyperlink10k | Split-development and split-test-hindsight fixed references | Frozen split-replay actions | Split-local `O_TIH` | Dependent retrospective scale/route stress |
| Dense-standard | Dataset-conditioned `F_dev`; equal archived `F_TIH` | Historical 20-split adaptive replay | `O_TIH` | In-distribution five-dataset replay; dataset identity is legal state |

## Interval and range warning

The range fields in `paper_reproduction/inputs/table3_recoverability.csv`
are not one homogeneous confidence-interval family:

- FEVER uses resampling over shared-gold-page/normalized-claim components;
- Structured-v2 uses support-title-component resampling with learners and
  actions frozen after the grouped construction;
- MuSiQue reports the registered official-validation diagnostic interval;
- Hyperlink10k and Dense report their registered split-replay ranges.

The exact finite-ledger contrast is primary. Each task's native README and
reports specify the resampling unit and what was held fixed.

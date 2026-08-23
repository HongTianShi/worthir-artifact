# RQ4: Robustness

The released summaries keep three kinds of sensitivity analysis separate:

- 2Wiki-Structured is fully refit and reselected at three tested cost weights.
- Its canonical policy is then held fixed and rescored under 816 monotone cost
  schedules; this tests the declared cost family, not arbitrary costs.
- FEVER keeps the same trained quality predictor but recomputes routing
  decisions at each cost weight, whereas MuSiQue rescores the policy selected
  at its primary setting.

`data/structured_candidate_recurrence.csv` removes queries associated with the most
frequent candidate documents using a target-blind frequency rule and repeats
the complete out-of-fold fit. `data/model_and_fold_summary.csv` records
the learner-family and fold-assignment checks.

FEVER's candidate-sharing graph forms one component over all 13,332 evaluation
queries, and every evaluation query shares at least one candidate with the
development set. A candidate-disjoint refit is therefore unavailable in this
construction. Candidate IDs are not router features; the result diagnoses
dependence rather than direct use of candidate identity.

# Frozen RQ2 Actions

This directory stores route selections or action-level inputs for the matched policy comparison.

The files cover ARR-style actions, non-neural actions, FEVER three- and five-route comparisons, and expected-cost random-control probabilities. Actions are frozen before evaluator outcomes are joined. File formats differ because they preserve the native outputs of the contributing analyses.

Do not infer utility directly from these files; use the released evaluator results and the RQ2 reproduction command. If an action file is replaced, record which policy, route set, split, and run aggregation it represents.

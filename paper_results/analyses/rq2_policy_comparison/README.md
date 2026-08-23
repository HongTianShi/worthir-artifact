# RQ2: Policy Comparison

This package compares all policies within each task's full route menu and
primary cost setting. It includes the development-selected fixed route,
uniform random routing, a low-capacity QPP gate, the task's existing adaptive
policy, and a query-only BERT adaptation of Adaptive Re-Ranking (ARR). The ARR
rows are a protocol-faithful adaptation, not a reproduction of an upstream
checkpoint.

`actions/non_neural_actions.parquet` and `actions/arr_actions.parquet` contain
one route ID per query. `actions/expected_cost_control_probabilities.csv`
contains the route-independent maximum-entropy distributions whose expected
mean cost matches each learned policy. The per-query route outcomes used for
scoring remain under `replays/`.

`actions/fever_same_menu_actions.csv` adds the three-route ExtraTrees action
vector, and `actions/fever_arr_3_and_5_route_actions.csv` contains the five
ARR seeds for both FEVER menus. Together with the cross-task action files they
reproduce all six rows in the FEVER three-/five-route comparison.

Primary statistical intervals use the task's dependence unit. Six contrasts
per task form one Holm family: QPP, the existing adaptive policy, and the
primary ARR seed versus (i) the fixed route and (ii) the corresponding
expected-cost-matched random allocation.

The expected-cost control preserves expected mean cost, not route frequencies.
Consequently, a policy's advantage over that control combines its induced
route mixture and its query--route assignments. The separate FEVER
route-frequency-matched permutation in `results/fever_query_route_matching.csv`
holds route counts fixed and isolates the gain from matching those routes to
queries.

`results/fever_online_latency.csv` reports warm online means on an RTX 4070
Laptop GPU. Each mean includes BM25, routing-time feature construction, one
single-query router call, and the selected paid operation. It excludes index
construction, model loading, offline training, cold starts, and tail latency.

# Reading WorthIR outputs

## Policy comparison

`comparison.csv` and `comparison.md` report:

- **mean effectiveness:** the selected routes' task metric;
- **mean cost:** cumulative cost of the selected routes;
- **mean utility:** effectiveness minus lambda times cost;
- **Delta U vs. fixed:** utility difference from the development-selected fixed
  route;
- **mean regret:** difference from the best registered route for each query;
- **oracle match share:** fraction of queries where the policy selects that
  evaluator-only route.

The development-selected fixed route is a deployable reference. The per-query
oracle is not deployable and only measures opportunity within the registered
route set.

## Fixed routes and the Pareto curve

`fixed_routes.csv` reports every fixed route. `pareto=true` means that no other
fixed route has both at least as much mean effectiveness and no greater mean
cost, with one strict improvement.

An adaptive policy is a query-weighted mixture of routes and need not coincide
with a fixed-route point.

## Scope of the generic report

The generic comparison is descriptive. It does not infer confidence intervals,
select a lambda, or claim transfer across tasks. Add resampling only when its
unit matches the task's dependence structure and the policy was frozen before
evaluation outcomes were joined.

## Organizer-only query rows

`worthir analyze TASK` writes `organizer_private/per_query_scores.csv`. Each row
contains the selected route's effectiveness, cost, and utility; the
development-selected fixed route; the within-route-set oracle; regret; and one
of three opportunity strata. This file contains query identifiers and
evaluator outcomes. It must not be supplied to a router or copied into
`participant/`.

The aggregate `worthir score` response remains participant-safe and does not
return query identifiers.

## Lambda sensitivity and hard budgets

`worthir sensitivity TASK` writes one row per lambda with policy, fixed-route,
and oracle utility. The policy actions remain frozen; only evaluator-side
utility arithmetic changes.

`worthir budget TASK` treats each declared value as a hard per-query cumulative
cost ceiling. It reports the evaluator-only effectiveness envelope among
feasible routes, the frozen policy's feasible share, and the development-fixed
route's feasible share. It does not silently replace an infeasible policy
action.

Both tables include `prespecified`, `scope`, and `interpretation`. A grid read
from the task contract is prespecified; a different command-line grid is not.

## Pareto SVG

`worthir plot TASK` writes `organizer_private/pareto.svg` without a plotting
dependency. Blue points are fixed routes, the blue line joins nondominated
fixed-route points, and the orange diamond is the frozen policy mean. The plot
is descriptive and evaluator-only.

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

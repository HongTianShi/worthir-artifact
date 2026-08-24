# Example contracts

These files define the six-query smoke test. For a new task, use
`worthir build-custom`, or use `worthir build-trec` for qrels and TREC runs;
both create a bound contract and route registry.

The public interface fixes five invariants: higher effectiveness is better, the
ledger contains every query--route pair, costs are nonnegative and cumulative,
their decision-time availability is explicit, and oracle ties prefer lower cost
then registry order. Fixed commitment-time costs live on registered routes;
query-dependent commitment-time costs live in `participant/route_costs.csv`.

# RQ3: Sources of Recoverable Utility

`query_strata.csv` partitions each evaluation set using the completed route
outcomes:

1. the cheapest route matches or exceeds every paid route in effectiveness;
2. a paid route improves effectiveness, but not enough to offset its cost;
3. a paid route is utility-improving.

The contribution column is the stratum's contribution to the policy's mean
utility gain over the development-selected fixed route. The contributions sum
to the task-level gain.

`top_decile_switching.csv` asks a narrower diagnostic question: can information
available at routing time identify queries for which the cheapest route is
already utility-optimal? Queries are ranked by the predicted probability of
that event; the top 10% switch from the fixed route to the cheapest route, and
all other queries retain the fixed route. The experiment measures utility
conversion, not only classification accuracy.

These strata and predictive diagnostics were defined after the original task
outcomes were available. They explain the observed gains rather than provide a
new confirmatory test.

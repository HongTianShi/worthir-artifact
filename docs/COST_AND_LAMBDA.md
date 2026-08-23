# Cost and lambda

WorthIR uses

```text
utility = effectiveness - lambda * cumulative_cost
```

The cost unit and lambda belong to the task definition. Utility is meaningful
within that task and cost profile; it is not a cross-dataset score.

## Choose a cost representation

Use the simplest representation that matches the deployment question:

- **Declared operator work:** assign cumulative relative costs such as 0, 0.25,
  and 1.00. State what each unit represents.
- **Measured latency:** use repeated warm measurements from the intended
  environment. Put per-query means in `costs.csv` when latency varies by query.
- **Model operations or energy:** use a consistent measured or computed unit and
  include all required preceding stages.

Do not mix unrelated units in one profile. A child route includes the cost of
its parents; it is not merely the incremental final-stage cost.

## Normalize only when it helps interpretation

Dividing every cost by a documented constant can make values readable. If raw
latency is divided by 100 milliseconds, for example, one cost unit means 100 ms.
Changing the cost scale requires the reciprocal change in lambda to preserve
the same utility preference.

## Choose lambda

Lambda says how much effectiveness the deployment is willing to exchange for
one cost unit. Choose it before examining evaluation outcomes. Suitable sources
include an operational service-level target, a development-set decision, or a
small set of declared preferences.

Report the primary lambda and inspect several plausible alternatives. A routing
claim that appears only at a narrow, post-hoc lambda should be described as
sensitivity rather than a general deployment result.

The example value `0.08` is illustrative. It is not a recommended default for a
new task.

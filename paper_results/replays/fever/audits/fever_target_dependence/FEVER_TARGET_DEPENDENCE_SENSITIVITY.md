# FEVER target and dependence sensitivity

Decision: **PASS as a frozen-outcome sensitivity.**

No route was rerun and no learner was fitted or selected. The registered
NDCG-trained legal action vectors were rescored against the archived complete
evidence-set success indicator.

## Dependence unit

- Queries: 13,332
- Components: 1,042
- Largest component: 133
- Singleton components: 1
- Definition: connected components induced by shared gold evidence page or identical normalized claim.

At lambda .08, the archived NDCG utility contrast is
0.011141. Its shared-page component-resampling range is
[0.009221,
 0.012846],
and its leave-one-component-out range is
[0.011016,
 0.011546].

## Verification-grounded target

Complete-set recall@10 equals one only when the ranking contains every page
from at least one valid official evidence set. At lambda .08:

- development-selected fixed route: ce100;
- test-hindsight fixed route: ce100;
- fixed utility: 0.867878;
- frozen legal-policy utility: 0.874684;
- evaluator oracle utility: 0.916679;
- legal-policy gain: 0.006806;
- headroom recovered: 13.95%;
- shared-page component-resampling range:
  [0.004176,
   0.009383].

## Claim policy

**Strongest defensible.** The positive FEVER acquisition result survives both
a verification-grounded complete-evidence-set target and resampling over
shared-gold-page dependence components.

**Conservative fallback.** The frozen NDCG-trained action vector retains
positive finite-ledger utility when rescored for complete evidence-set
success.

**Prohibited.** Population coverage, independence of FEVER claims, prospective
confirmation, or an official end-to-end FEVER verification score.

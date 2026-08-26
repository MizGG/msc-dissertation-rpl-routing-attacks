# Trust Layer V1 Results

This is an offline trust-aware representation, not yet an online RPL
defence. It tests whether trust-derived features add useful information
for concept drift and adaptation.

## Static Drift

- cart: zero recall 48/72, mean recall 0.2333, mean F1 0.1822.
- gaussian: zero recall 65/72, mean recall 0.0778, mean F1 0.0423.

## Adaptation

- 0 target seeds: mean recall 0.2333, mean F1 0.1822.
- 1 target seeds: mean recall 0.8056, mean F1 0.8258.
- 2 target seeds: mean recall 0.862, mean F1 0.8664.
- 3 target seeds: mean recall 0.8917, mean F1 0.8792.

## Interpretation

Compared with the non-trust routing-feature baseline, Trust Layer V1 does not
improve the CART cross-attack IDS metrics. The baseline already has access to
the underlying routing-window signals from which the trust scores are derived,
so the trust values do not add independent predictive information for this
model.

This should be reported as a useful negative result, not hidden. It shows that
adding a trust layer is not automatically enough to improve robustness under
concept drift. The value of V1 is interpretability and attack-surface diagnosis:
forwarding trust responds to blackhole/grayhole behaviour, rank trust responds
to sinkhole behaviour, control trust responds to DIS flood/Sybil behaviour, and
route trust responds to worst-parent behaviour.

It should not be claimed as a complete defence against Sybil or wormhole
attacks. Those attacks require stronger identity binding, topology plausibility
or timing evidence beyond this simple trust representation.

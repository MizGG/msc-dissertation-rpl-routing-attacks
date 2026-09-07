# Trust Layer Summary

Trust Layer V1 was implemented as an offline trust-aware feature layer over the
existing Cooja logs. It does not modify RPL parent selection yet.

The layer computes:

- forwarding trust;
- rank trust;
- control-message trust;
- route/topology trust;
- combined trust;
- component alert flags.

## Main Result

The trust-aware features did not improve the current CART cross-attack IDS
metrics compared with the existing routing-feature baseline:

| Scope | Baseline F1 | Trust F1 |
| --- | ---: | ---: |
| Static cross-attack | 0.1822 | 0.1822 |
| 1 target adaptation seed | 0.8258 | 0.8258 |
| 2 target adaptation seeds | 0.8664 | 0.8664 |
| 3 target adaptation seeds | 0.8792 | 0.8792 |

This is a defensible negative result. The trust scores are derived from signals
already present in the routing-window feature set, so they improve
interpretability more than predictive power.

## Attack-Surface Interpretation

- Blackhole and grayhole mainly reduce forwarding trust.
- Sinkhole triggers rank trust alerts.
- DIS flood and Sybil trigger control-message trust alerts.
- Worst-parent triggers control and route trust alerts.
- Wormhole remains weakly covered by this simple trust design.

## Dissertation Position

Trust Layer V1 should be presented as a diagnostic/explanation layer and a
stepping stone toward an online defence. It should not be claimed as a complete
defence against Sybil or wormhole attacks. A stronger version would need to
affect RPL parent selection and add identity/topology plausibility checks.

Evidence folder:

`experiments/trust_layer_v1`

# Trust Layer V1

This experiment implements the trust-layer idea as an offline feature
representation over the existing Cooja logs. It does not modify RPL parent
selection yet.

The purpose is to test whether a lightweight trust representation helps the IDS
under attack-distribution drift before spending time on an online routing
defence.

## Trust Components

- `trust_forwarding`: penalises reduced application response/forwarding
  behaviour relative to the pre-attack part of the same run.
- `trust_rank`: penalises suspicious low-rank non-root advertisements and wide
  rank ranges.
- `trust_control`: penalises abnormal RPL control-message volume and many DIO
  identities/senders.
- `trust_route`: penalises parent switching and unstable route/topology
  behaviour.
- `trust_total`: weighted score combining the components.

Weights:

- forwarding: 0.40
- rank: 0.25
- control: 0.20
- route: 0.15

This is intentionally conservative. The trust layer is used as additional IDS
representation, not as proof that every attack can be blocked by trust alone.

## Evidence

Run:

```sh
python3 experiments/trust_layer_v1/build_trust_features.py
python3 scripts/run_cross_attack_drift.py --features experiments/trust_layer_v1/features/trust_routing_window_features.csv --out-dir experiments/trust_layer_v1/results/static_drift
python3 scripts/run_cross_attack_adaptation.py --features experiments/trust_layer_v1/features/trust_routing_window_features.csv --out-dir experiments/trust_layer_v1/results/adaptation
python3 experiments/trust_layer_v1/summarise_trust_results.py
```

## Current Finding

Trust Layer V1 is useful as an explanation and diagnostic layer, but it does
not improve the current CART cross-attack IDS metrics compared with the
non-trust routing-feature baseline. This is not a failure of the dissertation
argument: it shows that these trust scores are mostly transformations of
signals already available to the model.

The useful result is attack-surface interpretation:

- blackhole and grayhole mainly reduce forwarding trust;
- sinkhole triggers rank trust alerts;
- DIS flood and Sybil trigger control-message trust alerts;
- worst-parent triggers control and route trust alerts;
- wormhole is weakly covered by this trust design.

The next version, if time allows, should be an online RPL parent-selection
penalty or a stronger identity/topology trust component. V1 should be presented
as a trust-aware feature/diagnostic layer, not as a complete defence.

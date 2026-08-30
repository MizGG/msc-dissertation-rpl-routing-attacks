# Cross-Attack Drift With Sybil

This experiment extends the earlier eight-family cross-attack drift matrix with
the new Sybil attack surface.

Inputs:

- blackhole and sinkhole routing-window features;
- additional professor-paper attack features: DIS flood, grayhole,
  increase-rank, DIO suppression, worst-parent and wormhole;
- new Sybil attack/control features from `experiments/sybil_attack_v1`.

The primary IDS feature set excludes simulator attack-marker fields such as
`*_enabled_events`, drop/send/selection markers and Sybil spoofing markers. The
marker columns remain in raw feature CSVs for validation and diagnosis only.

## Result

- Families evaluated: 9.
- Static CART cross-attack pairs: 72.
- CART zero-recall cross-attack pairs: 48.
- CART cross-attack pairs with F1 >= 0.8: 6.
- Sybil-related CART cross-attack pairs: 16.
- Sybil-related zero-recall pairs: 11.
- Sybil-related pairs with F1 >= 0.8: 3.

Interpretation: adding Sybil strengthens the concept-drift argument. Several
models trained on existing RPL attack families fail to detect Sybil attack
windows, showing that the changed attack surface is not captured by a static
model trained on earlier behaviour.

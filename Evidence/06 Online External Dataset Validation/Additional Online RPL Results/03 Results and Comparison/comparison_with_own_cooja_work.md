# External RPL Dataset Validation — Comparison with Dissertation Cooja Work

## What is directly comparable

Both studies use held-out attack environments and evaluate static detection before limited target-attack adaptation.
The metric names are comparable; raw fields, simulator, topology and split units are not.

## Existing Cooja reference

The existing routing-aware CART test trained on Cooja Blackhole and tested on Cooja Sinkhole reported F1=0.0000, recall=0.0000, accuracy=0.7222.
This is the original within-platform concept-drift finding, not an external benchmark.

## External static-transfer findings

- HUNSR: static_version_to_decreased_rank — F1=0.0102, recall=0.0350, accuracy=0.8084.
- HUNSR: static_version_to_dis_flood — F1=0.0388, recall=0.0882, accuracy=0.7962.
- HUNSR: static_version_to_selective_forwarding — F1=0.0498, recall=0.1382, accuracy=0.8052.
- RADAR: static_blackhole_to_sybil — F1=0.0000, recall=0.0000, accuracy=0.4808.
- RADAR: static_sybil_to_blackhole — F1=0.0000, recall=0.0000, accuracy=0.8117.

## Limited-target adaptation results

- RADAR Blackhole → Sybil: F1 0.0000 → 0.3158; recall 0.0000 → 0.4839 after 20% labelled target evidence.
- RADAR Sybil → Blackhole: F1 0.0000 → 0.3191; recall 0.0000 → 0.5172 after 20% labelled target evidence.
- HUNSR Version → Decreased Rank: F1 0.0102 → 0.1211; recall 0.0350 → 0.4347 after 20% labelled target evidence.
- HUNSR Version → DIS Flood: F1 0.0388 → 0.2479; recall 0.0882 → 0.7354 after 20% labelled target evidence.
- HUNSR Version → Selective Forwarding: F1 0.0498 → 0.0595; recall 0.1382 → 0.1660 after 20% labelled target evidence.

## Correct interpretation

A low static-transfer F1 indicates distribution and/or mechanism shift. A higher adapted F1 shows that limited labelled target evidence can help in that external representation.
These results do not establish a single model transferred from Cooja to NetSim: there is no defensible one-to-one raw feature schema. They are an external replication of the static-versus-adapted methodology.
RADAR is NetSim packet traffic; UOS is Cooja packet traffic; HUNSR is Contiki-NG/Cooja-derived behavioural data. HUNSR temporal rows lack a published run identifier, so its temporal split is more conservative than random rows but is not equivalent to a whole-run split.

# Robustness Campaign V1 Summary

## Purpose

This campaign checks whether the validated Blackhole, Sinkhole, and Sybil
attack implementations still execute and produce observable evidence under two
small Cooja sensitivity changes. It does not replace the original baseline
campaigns and it does not claim physical IoT testbed validation.

## Conditions

- `ATTACKER_RELOCATED`: node 16 is moved from `(65, 75)` to `(80, 75)` while the
  original radio range is retained.
- `LOSSY_RADIO`: the original node layout is retained, but UDGM receive success
  is reduced to `0.85`.

Each condition uses five seeds with matched attack/control runs for Blackhole,
Sinkhole, and Sybil.

## Validation Result

All 60 generated configurations completed with `TEST OK`, produced a
`COOJA.radio` log, and matched the expected attack-marker rule.

| Condition | Family | Valid runs | Attack marker count | Control marker count |
| --- | --- | ---: | ---: | ---: |
| ATTACKER_RELOCATED | Blackhole | 10/10 | 2096 | 0 |
| ATTACKER_RELOCATED | Sinkhole | 10/10 | 5 | 0 |
| ATTACKER_RELOCATED | Sybil | 10/10 | 745 | 0 |
| LOSSY_RADIO | Blackhole | 10/10 | 2101 | 0 |
| LOSSY_RADIO | Sinkhole | 10/10 | 5 | 0 |
| LOSSY_RADIO | Sybil | 10/10 | 745 | 0 |

## Interpretation

The result supports a limited robustness claim: the three core attack
implementations remain operational and observable when the attacker position is
changed and when the simulated radio channel is less ideal. This strengthens the
experimental evidence beyond a single fixed topology.

The result should not be described as a full deployment validation. It remains a
Cooja-based simulation check, and the IDS concept-drift conclusions still depend
on the feature extraction and classifier/adaptation experiments.

## Frozen IDS Sensitivity Check

The established routing-window parser extracted 540 windows from the 60 runs.
A CART model trained on the original blackhole/sinkhole routing-window data was
evaluated on post-activation windows. Using only coarse traffic/radio features,
F1 was:

| Condition | Blackhole | Sinkhole | Sybil |
| --- | ---: | ---: | ---: |
| Attacker relocated | 0.8475 | 0.4545 | 0.7636 |
| Lossy radio | 1.0000 | 0.0000 | 0.0000 |

These are sensitivity results, not new headline IDS claims. The robustness
configurations did not enable the generic RPL telemetry required by the
routing-aware feature set, so its rows in `results/ids_evaluation.csv` are a
diagnostic of missing instrumentation, not valid routing-aware robustness
evidence. A proper rerun would regenerate configurations with RPL INFO logging
enabled.

## Reproduction

```bash
python3 experiments/robustness_campaign_v1/run_campaign.py
python3 experiments/robustness_campaign_v1/validate_campaign.py
```

The raw logs are stored under `experiments/robustness_campaign_v1/runs/`, and
the generated `.csc` files are stored under `experiments/robustness_campaign_v1/configs/`.

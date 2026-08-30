# Focused Cooja Robustness Campaign V1

This package is separate from the validated baseline evidence. It generates
new Cooja configurations for Blackhole, Sinkhole, and Sybil without modifying
their source applications, Contiki-NG, or original configurations.

## Conditions

- `attacker_relocated`: node 16 moves from `(65, 75)` to `(80, 75)`. It remains
  within the original 65 m range of the root but has a different neighbourhood.
- `lossy_radio`: original layout with UDGM receive success ratio `0.85`.

Each condition has five seeds and matched attack/control configurations for
each family. The campaign is intentionally limited to the three attacks needed
to test the dissertation's central cross-attack and Sybil arguments.

No physical-network claim is made. These are reproducible Cooja sensitivity
conditions only.

Run or resume the campaign and validate only after all logs exist:

```bash
python3 experiments/robustness_campaign_v1/run_campaign.py
python3 experiments/robustness_campaign_v1/validate_campaign.py
```

## Completed validation

The completed campaign contains 60/60 valid Cooja configurations:

- 30/30 valid under `ATTACKER_RELOCATED`
- 30/30 valid under `LOSSY_RADIO`
- controls produced zero attack markers in both conditions

See `results/campaign_validation.csv`, `results/condition_summary.csv`, and
`results_summary.md`.

## IDS Evaluation Note

`features/routing_window_features.csv` contains 540 extracted windows, and
`results/ids_evaluation.csv` records a frozen-model evaluation on
post-activation windows. The coarse-feature rows are usable as a sensitivity
check. The robustness configurations did not enable the generic
`LOG_CONF_LEVEL_RPL=LOG_LEVEL_INFO` telemetry used by the dedicated
routing-feature campaign. Routing-feature rows are therefore retained only to
expose this instrumentation gap, not as routing-aware robustness evidence.

# Robustness Campaign V4

This isolated Cooja campaign tests Blackhole, Sinkhole and Sybil under two
simulated sensitivity conditions. It does not modify the preserved baseline
evidence or Contiki-NG.

## Conditions

- `ATTACKER_RELOCATED`: node 16 moves from `(65, 75)` to `(80, 75)`.
- `LOSSY_RADIO`: the baseline layout is retained and UDGM receive success is
  reduced to `0.85`.

Each family/condition has five matched attack and five matched control runs.
All runs use delayed activation at 240 seconds and end after a 541-second Cooja
timeout so the 540-second evidence window completes cleanly.

## Telemetry and Source Isolation

Each v4 application has its own local source directory and Makefile. The
Makefiles enable `LOG_CONF_LEVEL_RPL=LOG_LEVEL_INFO`, allowing generic DIO,
rank and parent telemetry to be extracted without using attack-marker text as
an IDS feature.

The Sinkhole router uses the strong shared-flag form already validated in
`routing_features_v1`. The earlier weak-symbol-only local copy produced a
single rank-128 advertisement then reverted to rank 256 under Cooja dynamic
library loading. Those invalid generated runs are preserved under
`diagnostics/pre_strong_flag_runs/` and excluded from all v4 results.

## Outputs

- `runs/`: 60 validated final Cooja logs.
- `features/routing_window_features.csv`: 540 60-second windows.
- `results/campaign_validation.csv`: completion and attack-marker validation.
- `results/ids_evaluation.csv`: frozen-model sensitivity evaluation.
- `results/adaptation_detail.csv`: every whole-seed adaptation split.
- `results/adaptation_summary.csv`: mean metrics over seed combinations.
- `results_summary.md`: bounded interpretation for dissertation use.

## Reproduction

```bash
python3 experiments/robustness_campaign_v4/generate_configs.py
python3 experiments/robustness_campaign_v4/run_campaign.py
python3 experiments/robustness_campaign_v4/validate_campaign.py
python3 scripts/extract_routing_window_features.py \
  --runs-dir experiments/robustness_campaign_v4/runs \
  --out experiments/robustness_campaign_v4/features/routing_window_features.csv \
  --expected-runs 60
python3 experiments/robustness_campaign_v4/evaluate_ids.py
python3 experiments/robustness_campaign_v4/evaluate_adaptation.py
```

This is a Cooja sensitivity experiment, not physical-IoT deployment validation.

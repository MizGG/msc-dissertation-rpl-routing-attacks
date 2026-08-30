# Robustness Campaign

This Cooja campaign tests Blackhole, Sinkhole and Sybil under two conditions: attacker relocation and lower radio reception probability (`0.85`).

Each family and condition has five attack and five control runs. Attacks start at 240 seconds and the simulations finish after the 540-second evidence window.

The local applications expose generic RPL rank and parent telemetry for feature extraction. Attack markers are not used as IDS features.

The outputs include 60 validated runs, 540 routing windows, campaign validation, frozen-model results and whole-seed adaptation summaries.

```sh
python3 experiments/robustness_campaign_v4/generate_configs.py
python3 experiments/robustness_campaign_v4/run_campaign.py
python3 experiments/robustness_campaign_v4/validate_campaign.py
```

These are Cooja sensitivity tests, not physical deployment tests.

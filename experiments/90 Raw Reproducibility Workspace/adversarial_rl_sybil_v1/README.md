# Local Adaptive IDS and Sybil Extension V1

This package is intentionally isolated from the established dissertation
evidence. It reads validated Cooja routing-window CSV files and writes all new
datasets, models, metrics and figures under this directory. It does not modify
Contiki-NG, preserved experiment folders, or existing dissertation results.

## Local-Only Reproducibility

The package makes no network requests and requires no credentials, hosted
service, external agent, or language model. It runs from a normal VS Code
terminal after Python 3.9+ is installed.

The DQN/DDQN controller uses the optional local PyTorch dependency listed in
`requirements-local.txt`. The standard-library baselines, stream construction,
drift monitors and tabular Q-learning controller remain runnable without it.

## Scope

The package evaluates a Cooja-based adaptive IDS extension inspired by, but not
an exact reproduction of, the NetSim adversarial-RL paper. The data source is
the validated 16-node Cooja campaign:

- Blackhole: forwarding/data-plane attack;
- Sinkhole: RPL rank manipulation;
- Sybil: RPL DIO source-identity manipulation.

Each stream is ordered by its existing 60-second windows. Cooja attack markers
are retained in the raw stream for validation only and excluded from all IDS,
drift, adversarial-selection and RL-controller feature sets.

## Package Layout

- `data/`: generated local stream datasets and manifests;
- `code/`: Cooja-specific Sybil sensitivity and defence artefacts, stored
  separately until built and run;
- `results/`: generated metrics and traces;
- `scripts/`: package-local runner entry points;
- `docs/`: methodology, limitations and experiment records.

## First Reproduction Command

From the repository root:

```bash
python3 scripts/build_adaptive_sybil_stream.py
```

This command creates `data/stream_windows.csv` and `data/feature_manifest.json`
from the validated evidence without changing its source files.

## Headless Cooja Run

The runner is local-only and preserves raw logs under `runs/`:

```bash
python3 experiments/adversarial_rl_sybil_v1/run_cooja_config.py \
  experiments/adversarial_rl_sybil_v1/configs/SYBIL_LOW_RATE_ATTACK_N16_SEED123456.csc \
  --run-dir experiments/adversarial_rl_sybil_v1/runs/SYBIL_LOW_RATE_ATTACK_N16_SEED123456
```

Run the isolated rate campaign and validate it with:

```bash
python3 experiments/adversarial_rl_sybil_v1/run_sybil_rate_campaign.py
python3 experiments/adversarial_rl_sybil_v1/validate_sybil_rate_campaign.py
python3 experiments/adversarial_rl_sybil_v1/summarize_sybil_rate_campaign.py
python3 experiments/adversarial_rl_sybil_v1/evaluate_identity_consistency.py
python3 experiments/adversarial_rl_sybil_v1/evaluate_sybil_identity_monitor.py
```

The checked-in campaign contains five seeds per attack rate and five shared
controls. Its summary reports only directly observed log and radio counts; it
does not infer a detection rate or claim a Sybil mitigation.

## Claim Boundary

The resulting experiments are controlled Cooja analyses, not a physical IoT
deployment and not a claim of universal operational robustness. A future Cooja
campaign may add radio-loss and topology sensitivity, but no unrun configuration
is reported as evidence.

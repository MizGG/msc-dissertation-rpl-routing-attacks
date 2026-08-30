# Adaptive IDS and Sybil Extension

This folder contains the adaptive IDS work built from validated Cooja routing windows for Blackhole, Sinkhole and Sybil. It is separate from the baseline campaigns and does not change Contiki-NG.

The data is arranged in 60-second windows. Attack markers are retained for run checks but excluded from the IDS, drift and controller features.

The package includes standard incremental baselines, River models with ADWIN, tabular profile selection and local DQN/DDQN controllers. PyTorch is optional; the basic stream and baseline work runs with Python 3.9 or later.

The RL work is an offline Cooja-derived experiment, inspired by the NetSim paper. It is not a live controller for Cooja or a physical IoT deployment.

Start by building the local stream:

```sh
python3 scripts/build_adaptive_sybil_stream.py
```

# Adaptive and RL Model Scope

## Why the RL Environment Is Offline

The validated Cooja runs are fixed recorded attack/control profiles. The
adversarial environment therefore selects complete profiles produced by Cooja;
it does not invent traffic values, modify packets, or control a live Cooja
simulation at every 60-second window. This is an offline adversarial
profile-selection environment.

The defender observes only generic non-marker routing features and delayed
labels. During training, rewards are calculated from the stored ground truth.
During evaluation, all target test seeds are held out from DQN/DDQN training.

## What Is Evaluated

- static source-trained detector;
- delayed-label incremental detector;
- River Hoeffding Tree and Gaussian NB with River ADWIN monitoring;
- tabular adversarial profile selection;
- local DQN and Double DQN policy controllers that decide whether to keep the
  source model, incrementally learn delayed labelled data, or rebuild from the
  labelled target history.

## What Is Not Claimed

- An exact replication of the NetSim ARL architecture;
- an online model deployed on a physical IoT network;
- an attacker that dynamically controls Cooja radio packets in real time;
- that a short nine-window stream is sufficient for universal ADWIN behaviour.

## Data Separation

The first three target seeds are used only for RL/adversarial policy training.
The last two target seeds are held out for evaluation. Seed boundaries are
preserved in all traces. The ordering is a deterministic experimental schedule,
not evidence that simulation seed values encode real time.

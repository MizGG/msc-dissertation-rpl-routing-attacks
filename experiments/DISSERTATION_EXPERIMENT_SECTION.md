# Controlled RPL Attack Dataset and Concept Drift Experiment

## Aim

This experiment evaluates how a baseline intrusion-detection model behaves when the malicious behaviour in an RPL/6LoWPAN network changes. The purpose is not only to implement routing attacks in Cooja, but to use those attacks as controlled data-generating conditions for studying concept drift in IoT cybersecurity data.

The experiment addresses the following question:

> If an IDS learns to distinguish normal traffic from one RPL attack family, does it still detect malicious behaviour when the attack mechanism changes?

## Experimental Environment

The experiments were conducted using Contiki-NG and the Cooja network simulator. Each simulation used a 16-node RPL/6LoWPAN topology with UDP client/server traffic and matched attack/control configurations. The attack activation time was fixed at 240 seconds and each simulation ran for 540 seconds. Five random seeds were used for each attack condition, with corresponding control runs for the same seeds.

Two attack families were used:

- Blackhole: the malicious node participates in routing and then drops forwarded traffic after activation.
- Sinkhole: the malicious node advertises an artificially attractive RPL rank after activation, while preserving its real internal RPL rank.

The sinkhole implementation uses a shared attack flag, `sinkhole_attack_enabled`, exposed to the RPL DIO advertisement path. When enabled, the node advertises `RPL_MIN_HOPRANKINC` as its rank in outgoing DIO messages. The node's internal RPL rank is not overwritten. This distinction is important because the experiment manipulates the network's routing advertisement behaviour without corrupting the node's internal routing state.

## Evidence Packages

The final blackhole evidence is stored in:

`experiments/blackhole/final_corrected_240s_540s/`

The final sinkhole evidence is stored in:

`experiments/sinkhole/final_corrected_240s_540s/`

Each final evidence package contains the application source files, Cooja configurations, simulation logs, radio logs, run directories, validation summary, and checksum manifest. This makes the simulation evidence auditable and reproducible from the preserved project state.

## Feature Extraction

Run-level features were extracted from the complete Cooja logs rather than splitting individual log lines randomly across train and test sets. This avoids leakage where traffic from the same simulation run could appear in both training and evaluation data.

The extracted dataset is stored in:

`experiments/features/run_level_features.csv`

It contains 20 complete simulation runs:

- 5 blackhole attack runs
- 5 blackhole control runs
- 5 sinkhole attack runs
- 5 sinkhole control runs

The baseline model uses traffic and log-volume features such as received UDP requests, received UDP responses, unreachable destinations, radio transmissions, and total log counts. Explicit attack-marker fields, such as sinkhole rank-advertisement log counts and blackhole attack log counts, were excluded from model training to reduce label leakage.

## Baseline IDS

A lightweight random-forest-style baseline classifier was implemented in pure Python so that the result does not depend on external machine-learning libraries being installed on the experimental machine. The classifier operates on complete-run feature rows and predicts a binary label:

- 0: control / normal run
- 1: attack run

The baseline script is stored in:

`scripts/run_baseline_ids.py`

The result table is stored in:

`experiments/ml_baseline/baseline_results.csv`

## Evaluation Design

Two evaluation settings were used.

First, the model was evaluated under same-family blackhole conditions. Leave-one-seed testing was used: for each seed, the model trained on the other blackhole attack/control runs and tested on the held-out attack/control pair. This checks whether the extracted features can distinguish blackhole attack runs from matched controls when the attack family remains stable.

Second, the model was trained on all blackhole attack/control runs and then tested on all sinkhole attack/control runs. This represents a cross-attack concept drift setting: the model has learned one malicious routing behaviour, then the malicious behaviour changes to a different RPL attack mechanism.

## Results

| Evaluation | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Blackhole same-family validation | 1.00 | 1.00 | 1.00 | 1.00 |
| Train on blackhole, test on sinkhole | 0.50 | 0.00 | 0.00 | 0.00 |

Under same-family blackhole validation, the model separated attack and control runs correctly. This shows that the Cooja-generated blackhole evidence contains a detectable traffic pattern under stable training and testing conditions.

Under the cross-attack evaluation, performance collapsed. The model achieved 0.50 accuracy, but this was because it classified the sinkhole attack runs as normal while correctly classifying the sinkhole control runs. The recall for attack detection was 0.00, meaning the model failed to detect any sinkhole attack runs after being trained only on blackhole behaviour.

## Interpretation

The result demonstrates concept drift at the attack-behaviour level. The data-generating environment remains within the same broad domain, RPL/6LoWPAN routing in Cooja, but the malicious mechanism changes from blackhole packet dropping to sinkhole rank manipulation. A model trained on the first attack family does not generalise to the second.

This supports the dissertation's central argument: IDS performance cannot be assumed to remain stable when IoT attack behaviour evolves. A detector may perform well under one known malicious pattern while failing against a different attack mechanism that changes the network distribution.

## Limitations

The current dataset is intentionally small: five seeds per attack/control condition. This is sufficient for a controlled proof-of-concept drift demonstration, but not for broad claims about real-world IDS performance. The features are also coarse run-level summaries, not packet-level or temporal-window features. Future work should expand the dataset with additional attack families, external IoT datasets, and adaptive learning experiments.

The Cooja-generated data should therefore be described as a controlled experimental dataset rather than as a direct reproduction of any published dataset.

## Next Step

An initial adaptation experiment was then run by adding whole sinkhole seeds to the blackhole training set and evaluating only on held-out sinkhole seeds. The result did not recover sinkhole detection: mean F1 remained 0.00 after adding one, two, or three sinkhole seeds.

This negative adaptation result is useful because it identifies the current bottleneck. The coarse run-level traffic features capture blackhole packet-dropping behaviour, but they do not capture sinkhole rank-manipulation behaviour in a useful non-leaking way. The next experimental step is therefore not simply to change the classifier, but to improve the feature representation using temporal-window, routing-parent, rank, DIO/DAO, or topology-change features that can expose sinkhole behaviour without relying on explicit attack log markers.

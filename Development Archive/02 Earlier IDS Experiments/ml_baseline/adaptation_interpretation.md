# Adaptation Experiment Interpretation

Input: `experiments/features/run_level_features.csv`

The adaptation experiment tests whether adding limited sinkhole evidence to the original blackhole training data restores sinkhole attack detection. Splits are made by whole sinkhole seed: when a seed is used for adaptation, both its attack and control runs are excluded from evaluation.

## Result

| Sinkhole seeds used for adaptation | Evaluation splits | Mean accuracy | Mean recall | Mean F1 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1 | 0.50 | 0.00 | 0.00 |
| 1 | 5 | 0.50 | 0.00 | 0.00 |
| 2 | 10 | 0.50 | 0.00 | 0.00 |
| 3 | 10 | 0.50 | 0.00 | 0.00 |

Adding sinkhole runs to the training set does not improve detection with the current coarse run-level feature set. The classifier continues to label held-out sinkhole attack runs as control/normal.

## Why This Happens

`feature_diagnostics.csv` shows that blackhole attack runs differ strongly from blackhole controls in traffic-volume features. For example, mean received responses drop from 694.4 to 276.0 and mean radio transmissions drop from 8984.4 to 5594.8.

Sinkhole attack runs do not show the same traffic-volume separation from sinkhole controls. Mean received responses are 695.0 for sinkhole attacks and 694.4 for sinkhole controls. Mean radio transmissions are also very close: 9000.2 for sinkhole attacks and 8984.4 for controls.

This means the present baseline features capture blackhole packet-dropping behaviour, but they do not capture sinkhole rank-manipulation behaviour in a useful non-leaking way.

## Dissertation Interpretation

This is still a defensible result:

1. The static blackhole-trained IDS fails under the blackhole-to-sinkhole attack-distribution change.
2. Simple retraining with a few whole sinkhole seeds does not recover performance when the feature representation is too coarse.
3. The next scientific improvement is feature engineering, especially temporal-window, routing-parent, rank, DIO/DAO, or topology-change features that can represent sinkhole behaviour without relying on explicit attack log markers.

This should be presented as evidence that adaptation is not only a model problem. The feature representation must expose the changed attack mechanism.

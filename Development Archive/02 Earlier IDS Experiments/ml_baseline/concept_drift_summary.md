# Concept Drift Baseline Summary

Input: `experiments/features/run_level_features.csv`

Model: pure-Python random-forest-style classifier using complete-run traffic features only. Attack-marker fields are excluded to avoid label leakage.

Key result:

| Experiment | Accuracy | Precision | Recall | F1 | TP | TN | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Blackhole leave-seed CV | 1.00 | 1.00 | 1.00 | 1.00 | 5 | 5 | 0 | 0 |
| Train blackhole, test sinkhole | 0.50 | 0.00 | 0.00 | 0.00 | 0 | 5 | 0 | 5 |

Interpretation: the detector learns the blackhole attack pattern under same-family evaluation, but fails to identify sinkhole attack runs when evaluated cross-family. This gives a compact concept-drift result: a model trained on one RPL attack behaviour does not generalise to a structurally different RPL attack, even though both are malicious.

This should be treated as the baseline drift demonstration before adding explainability or LLM interpretation.

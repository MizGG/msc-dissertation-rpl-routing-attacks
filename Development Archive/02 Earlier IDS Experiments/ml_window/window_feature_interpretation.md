# Window-Level Concept Drift Interpretation

Input: `experiments/features/window_features.csv`

The window feature extractor converts each final Cooja run into 60-second windows. Attack-run windows before 240 seconds are labelled normal, and attack-run windows from 240 seconds onward are labelled attack. Explicit attack-marker columns are preserved for validation but excluded from IDS model features.

## Why This Was Needed

The first run-level IDS result showed that blackhole traffic-volume effects are easy to detect, but sinkhole rank manipulation is not visible in coarse whole-run traffic summaries. This window-level experiment tests whether pre/post timing, app counter deltas, radio activity and RPL parent/no-parent events expose more of the controlled attack-distribution change.

## Static Model Result

| Evaluation | Accuracy | Precision | Recall | F1 | F2 | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Blackhole leave-seed windows | 0.99 approx. | 1.00 | 0.96 approx. | 0.98 approx. | 0.97 approx. | 0.00 |
| Train blackhole windows, test sinkhole windows | 0.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

The blackhole window model performs well in-domain. When frozen and evaluated on sinkhole windows, it still detects no sinkhole attack windows. The higher accuracy compared with the run-level result is caused by class imbalance at window level: pre-activation windows and controls are normal, so predicting normal for all sinkhole windows gives 65/90 correct.

## Adaptation Result

| Sinkhole seeds used for adaptation | Mean accuracy | Mean precision | Mean recall | Mean F1 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0.7222 | 0.0000 | 0.0000 | 0.0000 |
| 1 | 0.7222 | 0.0000 | 0.0000 | 0.0000 |
| 2 | 0.7074 | 0.0000 | 0.0000 | 0.0000 |
| 3 | 0.4944 | 0.3547 | 1.0000 | 0.5237 |

Adding one or two sinkhole seeds still does not recover detection. With three sinkhole seeds, the model finds the held-out sinkhole attack windows, but at the cost of many false positives. This is a useful tradeoff result rather than a clean recovery result.

## Dissertation Interpretation

The window-level features strengthen the evidence chain:

1. The IDS works on in-domain blackhole windows.
2. The frozen blackhole-trained IDS still fails on sinkhole attack windows.
3. Limited adaptation only helps after enough sinkhole seeds are provided, and the recovery is recall-heavy with poor precision.
4. Better routing-specific features are still needed for defensible sinkhole detection.

This supports the central concept-drift argument: when the attack mechanism changes, the learned decision boundary and the feature representation both matter. Retraining alone is not guaranteed to recover performance unless the features expose the new behaviour.

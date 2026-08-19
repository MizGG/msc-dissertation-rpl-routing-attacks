# Dissertation Results So Far

## Controlled Attack-Distribution Shift

The IDS was first evaluated under stable blackhole conditions and then under a controlled change from blackhole packet dropping to sinkhole rank manipulation. All Cooja train/test partitions were separated by complete simulation seed. Attack markers used to verify activation were excluded from classifier features.

| Dataset and evaluation | Accuracy | Precision | Recall | F1 | F2 | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Cooja run, blackhole in-domain | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Cooja run, static blackhole to sinkhole | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Cooja window, blackhole in-domain | 0.9889 | 1.0000 | 0.9600 | 0.9796 | 0.9677 | 0.0000 |
| Cooja window, static blackhole to sinkhole | 0.7222 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Cooja window, three-seed adaptation (mean) | 0.4944 | 0.3547 | 1.0000 | 0.5237 | 0.7332 | 0.7000 |
| Cooja routing CART, static blackhole to sinkhole | 0.7222 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Cooja routing CART, coarse three-seed adaptation | 0.7222 | 0.3083 | 0.0600 | 0.0978 | 0.0709 | 0.0231 |
| Cooja routing CART, routing-aware three-seed adaptation | 0.9861 | 1.0000 | 0.9500 | 0.9731 | 0.9588 | 0.0000 |
| Gope rows, static blackhole to sinkhole | 0.5083 | 0.6067 | 0.0472 | 0.0876 | 0.0579 | 0.0306 |

The strong blackhole results demonstrate that the experimental pipeline can learn a stable in-domain signal. When the frozen detector was transferred to sinkhole data, attack recall fell to zero at both run and window resolutions. Window accuracy remained 0.7222 only because 65 of the 90 evaluation windows were labelled normal; the confusion matrix was TN=65, FN=25, TP=0 and FP=0. Accuracy is therefore not evidence of detection in this condition.

## Adaptation

Adaptation data were added by complete sinkhole seed, and testing used only unseen seeds. The earlier coarse Gaussian window model obtained recall by over-alerting: with three adaptation seeds it had recall 1.0000 but FPR 0.7000. The routing-aware ablation isolates the reason. With three adaptation seeds, CART using coarse features achieved recall 0.0600 and F1 0.0978. Adding generic RPL routing-state features raised mean recall to 0.9500 and F1 to 0.9731, with precision 1.0000 and FPR 0 across the ten held-out-seed combinations.

This rejects the simplistic assumption that retraining alone resolves concept drift. The feature representation must expose the changed mechanism. Coarse application and radio-volume summaries show a pronounced blackhole effect but almost no sinkhole attack/control separation. Generic received-DIO rank and RPL-state features capture the persistent non-root rank-128 advertisement; they make limited, seed-separated adaptation effective.

## Online Drift Detection

A one-sided CUSUM monitor was calibrated on blackhole rank-state windows while excluding the matching seed, then applied to each complete sinkhole sequence in time order. It used only the stateful low-rank non-root pair, sender and receiver-exposure counts; labels and attack-marker fields were excluded from the monitor input. It detected 5 of 5 attack runs in the first post-activation window, with median delay 0 seconds and control-run false-alarm rate 0.0000.

This result should be described precisely: the monitor detects the controlled rank-state change in this five-seed Cooja experiment. Since blackhole reference scores are all zero, calibration uses a non-zero minimum decision limit. It demonstrates that the routing representation exposes a timely shift signal, but does not validate universal deployment-level drift detection.

## External Dataset Check

The supplied Gope collection contains 768,811 rows across eight attack files. Seven files include a supervised `TYPE` label and routing-aware fields; Worst Parent has no `TYPE` label and is excluded from the preliminary supervised baseline. A routing-aware Gaussian model trained on balanced blackhole rows and tested on balanced sinkhole rows achieved accuracy 0.5083, recall 0.0472 and F1 0.0876. The weak transfer is consistent with the Cooja finding, although the result is preliminary because the supplied CSVs do not provide simulation-run identifiers.

## Result Position

Taken together, the evidence shows a reproducible attack-distribution shift, static-model failure, and a routing-aware adaptation recovery under a seed-separated protocol. The next scientific task is a formal drift detector, evaluated against this now-established static-versus-adapted baseline; an LLM explanation layer should follow only after the detector is fixed.

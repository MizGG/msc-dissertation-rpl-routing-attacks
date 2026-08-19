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
| Gope rows, static blackhole to sinkhole | 0.5083 | 0.6067 | 0.0472 | 0.0876 | 0.0579 | 0.0306 |

The strong blackhole results demonstrate that the experimental pipeline can learn a stable in-domain signal. When the frozen detector was transferred to sinkhole data, attack recall fell to zero at both run and window resolutions. Window accuracy remained 0.7222 only because 65 of the 90 evaluation windows were labelled normal; the confusion matrix was TN=65, FN=25, TP=0 and FP=0. Accuracy is therefore not evidence of detection in this condition.

## Adaptation

Adaptation data were added by complete sinkhole seed, and testing used only unseen seeds. One or two sinkhole seeds produced no window-level detection. With three adaptation seeds, mean recall increased to 1.0000 and mean F1 to 0.5237, but mean FPR increased to 0.7000 and precision remained 0.3547. The adapted model therefore detected attack windows by labelling many normal windows as malicious. Run-level adaptation remained at zero recall for every tested adaptation size.

This result rejects the simplistic assumption that retraining alone resolves concept drift. The feature representation must expose the changed mechanism. Current application and radio-volume summaries show a pronounced blackhole effect but almost no sinkhole attack/control separation. Sinkhole detection requires routing-aware evidence such as advertised rank, preferred-parent changes, parent count, typed RPL control-message counts and hop-count changes.

## External Dataset Check

The supplied Gope collection contains 768,811 rows across eight attack files. Seven files include a supervised `TYPE` label and routing-aware fields; Worst Parent has no `TYPE` label and is excluded from the preliminary supervised baseline. A routing-aware Gaussian model trained on balanced blackhole rows and tested on balanced sinkhole rows achieved accuracy 0.5083, recall 0.0472 and F1 0.0876. The weak transfer is consistent with the Cooja finding, although the result is preliminary because the supplied CSVs do not provide simulation-run identifiers.

## Result Position

Taken together, the evidence shows a reproducible attack-distribution shift, static-model failure, and a measurable but operationally poor adaptation response. The immediate scientific task is to add non-leaking RPL routing-state features to the Cooja logs and rerun the same seed-separated protocol. Only after that feature milestone should a formal drift detector and LLM explanation layer be evaluated.

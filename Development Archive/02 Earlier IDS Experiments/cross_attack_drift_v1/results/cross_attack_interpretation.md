# Cross-Attack Concept Drift Notes

This experiment treats each attack family as a separate operating environment.
Models are trained on one attack/control family and tested on another family,
using whole Cooja runs and 60-second windows. Labels are used only for evaluation.

The main dissertation reading is not simply whether retraining works. The
important question is which feature representation transfers across changed
attack mechanisms and where it fails.

Total CART cross-attack pairs with zero attack recall: 37.
Total CART cross-attack pairs with F1 >= 0.8: 3.

Zero-recall pairs are useful evidence of concept drift/model brittleness:
- train blackhole -> test dio_suppression: accuracy=0.7222, recall=0.0, f1=0.0
- train blackhole -> test dis_flood: accuracy=0.7222, recall=0.0, f1=0.0
- train blackhole -> test grayhole: accuracy=0.7222, recall=0.0, f1=0.0
- train blackhole -> test sinkhole: accuracy=0.7222, recall=0.0, f1=0.0
- train blackhole -> test wormhole: accuracy=0.7222, recall=0.0, f1=0.0
- train blackhole -> test worst_parent: accuracy=0.7222, recall=0.0, f1=0.0
- train dio_suppression -> test blackhole: accuracy=0.7222, recall=0.0, f1=0.0
- train dio_suppression -> test sinkhole: accuracy=0.7222, recall=0.0, f1=0.0
- train dio_suppression -> test wormhole: accuracy=0.7222, recall=0.0, f1=0.0
- train dio_suppression -> test worst_parent: accuracy=0.6111, recall=0.0, f1=0.0
- train dis_flood -> test blackhole: accuracy=0.7222, recall=0.0, f1=0.0
- train dis_flood -> test dio_suppression: accuracy=0.7222, recall=0.0, f1=0.0
- train dis_flood -> test grayhole: accuracy=0.7222, recall=0.0, f1=0.0
- train dis_flood -> test increase_rank: accuracy=0.7222, recall=0.0, f1=0.0
- train dis_flood -> test sinkhole: accuracy=0.7222, recall=0.0, f1=0.0
- train dis_flood -> test wormhole: accuracy=0.7222, recall=0.0, f1=0.0
- train grayhole -> test dio_suppression: accuracy=0.7222, recall=0.0, f1=0.0
- train grayhole -> test dis_flood: accuracy=0.7222, recall=0.0, f1=0.0
- train grayhole -> test sinkhole: accuracy=0.7222, recall=0.0, f1=0.0
- train grayhole -> test wormhole: accuracy=0.7222, recall=0.0, f1=0.0
- plus 17 more zero-recall pairs in the CSV.

Methodological caution: attack-specific log marker features are excluded from
the default feature set because they would leak the simulator instrumentation
into the classifier. They are retained in the raw feature CSV for validation
and diagnosis, not for the primary IDS claim.

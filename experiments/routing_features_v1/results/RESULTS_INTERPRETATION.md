# Routing-Aware Adaptation Result

## Primary Result

The static blackhole-trained models still detect no sinkhole attack windows:
recall and F1 remain 0. This preserves the controlled attack-distribution-shift
result.

The routing-feature ablation changes adaptation performance substantially when
using CART:

| Sinkhole adaptation seeds | Feature set | Accuracy | Precision | Recall | F1 | F2 | FPR |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | coarse + routing | 0.7222 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 1 | coarse | 0.7250 | 0.2000 | 0.0100 | 0.0190 | 0.0123 | 0.0000 |
| 1 | coarse + routing | 0.9250 | 1.0000 | 0.7300 | 0.8129 | 0.7574 | 0.0000 |
| 2 | coarse + routing | 0.9648 | 1.0000 | 0.8733 | 0.9087 | 0.8857 | 0.0000 |
| 3 | coarse | 0.7222 | 0.3083 | 0.0600 | 0.0978 | 0.0709 | 0.0231 |
| 3 | coarse + routing | 0.9861 | 1.0000 | 0.9500 | 0.9731 | 0.9588 | 0.0000 |

With three complete sinkhole adaptation seeds, routing-aware CART improves mean
F1 from 0.0978 to 0.9731 and recall from 0.0600 to 0.9500, while reducing mean
FPR from 0.0231 to 0. The routing-state representation therefore enables
effective adaptation on held-out seeds; adding more examples to the coarse
representation does not.

## Mechanistic Evidence

Across post-activation sinkhole windows, the latest observed minimum non-root
rank is 128 for attack and 256 for control. Attack windows retain five
receiver/sender pairs exposed to a low-rank non-root advertisement; controls
retain zero. These fields derive from generic received-DIO logs rather than the
attack marker.

Gaussian Naive Bayes reaches full recall with routing features but retains high
FPR because its feature-independence assumption is unsuitable for the many
correlated routing counters. CART uses the discriminative routing-state split
without this over-alerting. This demonstrates that both representation and
model choice affect adaptation quality.

## Defensible Claim

The experiment supports a stronger but still bounded conclusion: the static IDS
fails after a controlled blackhole-to-sinkhole attack change, while limited
whole-seed adaptation succeeds when the representation exposes persistent RPL
rank state and the classifier can use that state appropriately. This does not
establish universal deployment performance; it is evidence from five matched
Cooja seeds and should be presented with that limitation.

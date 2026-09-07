# Robustness Campaign V4 Results

## Validation

All 60 final Cooja configurations completed with `TEST OK`, produced a radio
log, and satisfied their attack/control marker rule. Generic RPL telemetry was
enabled for every mote application.

Post-activation Sinkhole rank evidence confirms persistent manipulation:

| Condition | Attack low-rank non-root DIO events | Control events |
| --- | ---: | ---: |
| Attacker relocated | 339 | 0 |
| Lossy radio | 1139 | 0 |

## Frozen IDS Sensitivity

The frozen models are trained on the original Blackhole/Sinkhole routing-window
dataset, then evaluated on the new condition's post-activation attack/control
windows. CART with coarse features retains Blackhole detection but is unstable
for Sinkhole and Sybil after a condition change. Adding routing features makes
the Sinkhole mechanism visible, but can also make the frozen CART over-alert
when the distribution differs from its original condition.

The most important frozen CART results are:

| Condition | Family | Coarse F1 | Coarse+routing F1 | Qualification |
| --- | --- | ---: | ---: | --- |
| Attacker relocated | Blackhole | 0.8475 | 0.6667 | Routing model recalls all attacks but alerts on all controls. |
| Attacker relocated | Sinkhole | 0.5217 | 0.6667 | Routing model recalls all attacks but alerts on all controls. |
| Attacker relocated | Sybil | 0.7636 | 0.6667 | Routing model recalls all attacks but alerts on all controls. |
| Lossy radio | Blackhole | 1.0000 | 0.6667 | Routing model alerts on all controls. |
| Lossy radio | Sinkhole | 0.0000 | 1.0000 | Persistent rank state separates this condition cleanly. |
| Lossy radio | Sybil | 0.0000 | 0.6667 | Routing model alerts on all controls. |

Thus, this campaign strengthens the central claim rather than replacing it:
feature visibility is necessary, but a frozen decision boundary remains
sensitive to changed simulated conditions.

## Whole-Seed Adaptation

For each condition/family, target-family attack and control windows from one,
two or three complete seeds were added to the original training data. Evaluation
used only the remaining complete seeds. The following three-seed CART results
are means over ten seed combinations:

| Condition | Family | Feature set | Mean F1 | Mean recall | Mean FPR |
| --- | --- | --- | ---: | ---: | ---: |
| Attacker relocated | Blackhole | coarse | 1.0000 | 1.0000 | 0.0000 |
| Attacker relocated | Sinkhole | coarse+routing | 1.0000 | 1.0000 | 0.0000 |
| Attacker relocated | Sybil | coarse+routing | 0.9947 | 0.9900 | 0.0000 |
| Lossy radio | Blackhole | coarse | 1.0000 | 1.0000 | 0.0000 |
| Lossy radio | Sinkhole | coarse+routing | 1.0000 | 1.0000 | 0.0000 |
| Lossy radio | Sybil | coarse+routing | 0.9367 | 0.9800 | 0.0462 |

The condition-specific adaptation protocol is not an independent deployment
test: adaptation uses labelled examples from the same simulated condition.
Its defensible conclusion is narrower: limited, whole-seed labelled data from
the changed condition can restore performance when the corresponding attack
mechanism is represented in the features.

## Scope

This is a reproducible Cooja simulation sensitivity analysis. It does not show
physical-network robustness, universal cross-topology generalisation, or a
fully online deployed IDS.

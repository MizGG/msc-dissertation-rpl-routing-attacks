# Consolidated Concept-Drift Results

## Research Claim Supported by the Current Evidence

The experiments support a bounded claim: an IDS trained on blackhole behaviour does not reliably generalise when the malicious mechanism changes to sinkhole rank manipulation. This is a controlled attack-distribution shift used to evaluate concept drift; it is not evidence that every natural 6LoWPAN deployment will drift in the same way.

## Main Findings

1. **The baseline works before the attack change.** Whole-seed blackhole validation achieved perfect run-level detection. The 60-second model produced aggregate accuracy 0.9889, recall 0.9600 and F1 0.9796 across the five held-out blackhole seeds. This establishes that the pipeline can learn a stable in-domain attack signal.
2. **Static transfer fails after the attack mechanism changes.** The run-level blackhole model classified all five sinkhole attacks as normal, giving recall and F1 of 0. At window level, recall and F1 also remained 0. The apparent accuracy of 0.7222 is only the majority-class baseline: 65 of 90 sinkhole evaluation windows are normal, and the model predicted every window as normal.
3. **Simple adaptation is representation-limited.** Adding one, two or three complete sinkhole seeds did not improve the run-level model. At window level, three adaptation seeds raised mean recall to 1.0000 and mean F1 to 0.5237, but mean false-positive rate rose to 0.7000. The detector recovered sensitivity by over-alerting, so this cannot be described as successful adaptation without qualification.
4. **The supplied Gope data independently supports the transfer problem.** A preliminary routing-aware Gaussian model trained on Gope blackhole rows achieved only 0.0472 recall and 0.0876 F1 on Gope sinkhole rows. This is corroborating evidence, not a direct replication, because the supplied files expose no run identifiers and the current split is row-based.

## Mechanistic Interpretation

The negative result is explainable. Blackhole runs produce a large throughput and radio-volume change because forwarded traffic is dropped. In the extracted run-level features, mean received responses fall by 418.4 and mean radio transmissions by 3389.6 relative to matched controls. Sinkhole attack and control runs differ by only 0.6 received responses and 15.8 radio transmissions on average. The current Cooja representation therefore captures the blackhole consequence but not the sinkhole mechanism.

The Gope audit shows what is missing: rank, parent identity and count, typed DIO/DAO/DIS counters, hop count and packet loss. These are routing-state features with a defensible causal relationship to sinkhole behaviour. The next model milestone should instrument those signals in Cooja and then repeat exactly the same whole-seed static and adaptation evaluation.

## Validity Boundaries

- The Cooja dataset has five matched seeds per attack/control condition. This is adequate for a controlled proof of concept but too small for broad deployment claims.
- Adaptation and evaluation are separated by complete Cooja seed, preventing windows or runs from the same simulation entering both sets.
- Explicit blackhole and sinkhole log markers are excluded from model inputs; they are retained only to validate attack activation.
- The Gope baseline is preliminary because the source files lack run identifiers. Random row holdout may inflate in-domain performance, so it must not be presented as a final paper reproduction.
- Mean adaptation scores average overlapping combinations of held-out seeds. They describe sensitivity across the available seeds, not independent repeated trials.

## Defensible Dissertation Conclusion So Far

The strongest conclusion is not that retraining automatically solves drift. It is that adaptation depends on representation: when the feature space omits the changed attack mechanism, a static detector fails and naive retraining either remains ineffective or recovers recall at an unacceptable false-positive cost. That is a useful Master's-level finding because it links the observed model failure to RPL attack mechanics and produces a concrete, testable next step.

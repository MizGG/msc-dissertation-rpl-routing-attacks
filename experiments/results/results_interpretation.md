# Consolidated Concept-Drift Results

## Research Claim Supported by the Current Evidence

The experiments support a bounded claim: an IDS trained on blackhole behaviour does not reliably generalise when the malicious mechanism changes to sinkhole rank manipulation. This is a controlled attack-distribution shift used to evaluate concept drift; it is not evidence that every natural 6LoWPAN deployment will drift in the same way.

## Main Findings

1. **The baseline works before the attack change.** Whole-seed blackhole validation achieved perfect run-level detection. The 60-second model produced aggregate accuracy 0.9889, recall 0.9600 and F1 0.9796 across the five held-out blackhole seeds. This establishes that the pipeline can learn a stable in-domain attack signal.
2. **Static transfer fails after the attack mechanism changes.** The run-level blackhole model classified all five sinkhole attacks as normal, giving recall and F1 of 0. At window level, recall and F1 also remained 0. The apparent accuracy of 0.7222 is only the majority-class baseline: 65 of 90 sinkhole evaluation windows are normal, and the model predicted every window as normal.
3. **Coarse-feature adaptation is representation-limited.** The earlier Gaussian window model reached recall 1.0000 after three adaptation seeds, but its FPR rose to 0.7000. Routing-experiment CART with three seeds and coarse features remains weak (recall 0.0600, F1 0.0978).
4. **Routing-aware adaptation succeeds on held-out seeds.** Static routing-aware CART still has zero recall and F1 (0.0000 and 0.0000), preserving the drift finding. After three whole-seed adaptation runs, CART with routing features reaches accuracy 0.9861, precision 1.0000, recall 0.9500, F1 0.9731 and FPR 0.0000.
5. **The supplied Gope data independently supports the transfer problem.** A preliminary routing-aware Gaussian model trained on Gope blackhole rows achieved only 0.0472 recall and 0.0876 F1 on Gope sinkhole rows. This is corroborating evidence, not a direct replication, because the supplied files expose no run identifiers and the current split is row-based.

## Mechanistic Interpretation

The negative result is explainable. Blackhole runs produce a large throughput and radio-volume change because forwarded traffic is dropped. In the extracted run-level features, mean received responses fall by 418.4 and mean radio transmissions by 3389.6 relative to matched controls. Sinkhole attack and control runs differ by only 0.6 received responses and 15.8 radio transmissions on average. The current Cooja representation therefore captures the blackhole consequence but not the sinkhole mechanism.

The routing-aware experiment instruments generic RPL INFO logs for DIO/DAO/DIS traffic, received DIO ranks, parent switches, internal rank and neighbour state. Its stateful low-rank non-root features identify the altered mechanism without using attack-marker text. Corrected sinkhole runs consistently advertise rank 128 after activation, whereas controls retain rank 256. This is why routing-aware CART can adapt while coarse features cannot.

## Validity Boundaries

- The Cooja dataset has five matched seeds per attack/control condition. This is adequate for a controlled proof of concept but too small for broad deployment claims.
- Adaptation and evaluation are separated by complete Cooja seed, preventing windows or runs from the same simulation entering both sets.
- Explicit blackhole and sinkhole log markers are excluded from model inputs; they are retained only to validate attack activation.
- The Gope baseline is preliminary because the source files lack run identifiers. Random row holdout may inflate in-domain performance, so it must not be presented as a final paper reproduction.
- Mean adaptation scores average overlapping combinations of held-out seeds. They describe sensitivity across the available seeds, not independent repeated trials.

## Defensible Dissertation Conclusion So Far

The strongest conclusion is that adaptation depends on representation and model choice. A static detector fails under the controlled blackhole-to-sinkhole change even after routing features are added. Retraining with coarse features also remains ineffective. However, limited whole-seed adaptation with routing-state features and CART restores held-out sinkhole detection with high F1 and no observed false positives. This is a defensible Master's-level result because it ties model recovery to the RPL mechanism rather than claiming retraining is universally sufficient.

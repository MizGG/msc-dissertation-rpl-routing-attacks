# Dissertation Draft: RPL IDS Under Concept Drift

## Abstract Draft

This dissertation evaluates intrusion detection for RPL/6LoWPAN networks under
controlled attack-distribution change. A Contiki-NG/Cooja campaign was used to
validate nine RPL attack families: blackhole, sinkhole, DIS flood, grayhole,
increase-rank, DIO suppression, worst-parent, wormhole and Sybil. Each family
contains five attack runs and five matched control runs. The study then tests
whether static IDS models trained on one attack family generalise to another,
and whether limited whole-seed target adaptation can recover performance.

The results show that static IDS models are brittle under cross-attack concept
drift. For the CART model, 48 of 72 cross-attack train/test pairs produced zero
attack recall. Whole-seed adaptation substantially improved performance, with
mean CART F1 increasing from 0.1822 with no target-family seeds to 0.8258 with
one target seed and 0.8792 with three target seeds. Sybil identity manipulation
provides the main new attack-surface contribution: static Sybil-target F1 was
0.2183, while one Sybil adaptation seed increased held-out F1 to 0.9683.

The dissertation argues that IDS robustness under drift depends on both model
adaptation and feature representation. Retraining alone is insufficient when
the extracted features do not expose the changed attack mechanism. Trust and
LLM explanation layers are treated as interpretability components rather than
complete defences or detectors.

## 1. Introduction Draft

RPL is widely used for low-power and lossy IoT networks, where constrained
devices form multi-hop routing topologies. These networks are vulnerable to
routing attacks because malicious behaviour can affect forwarding, rank
advertisement, control-message behaviour, parent selection, topology structure
or node identity. Intrusion detection systems can identify known attacks, but a
static detector may fail when the attack environment changes.

This dissertation focuses on that problem. Instead of evaluating an IDS only on
a fixed train/test split from the same attack distribution, it constructs a
controlled concept-drift setting: the model is trained on one RPL attack family
and evaluated on another. This tests whether the detector has learned general
security behaviour or only the specific signals of the training attack.

The work makes four practical contributions. First, it implements and validates
a multi-attack Cooja campaign covering nine RPL attack families. Second, it
evaluates static cross-attack IDS transfer and shows frequent recall collapse.
Third, it evaluates whole-seed adaptation and shows that limited target-family
data can recover performance without random row leakage. Fourth, it adds Sybil
identity manipulation as a new attack surface and connects it directly to the
concept-drift and adaptation experiments.

## 2. Methodology

The methodology combines Contiki-NG/Cooja simulation, routing-window feature
extraction, static IDS evaluation, adaptation experiments, trust diagnostics
and an evidence-grounded explanation layer. The LLM is not used as the IDS.
Detection and drift evidence are produced first by the IDS and analysis
pipeline; explanations are a later interpretability layer.

The Cooja campaign uses matched attack and control configurations. Each attack
starts disabled, waits until 240 seconds and then activates. The full
simulation duration is 540 seconds, which provides a pre-attack baseline and
five 60-second post-activation windows. The validated dataset contains nine
attack families, each with five attack seeds and five matched control seeds,
for 90 validated Cooja runs.

The attack set is mechanism-diverse. Blackhole and grayhole affect forwarding
behaviour; sinkhole and increase-rank affect rank incentives; DIS flood and DIO
suppression affect control-plane dynamics; worst-parent affects route
selection; wormhole affects topology plausibility; and Sybil affects the
identity surface by rotating the apparent source identity used for RPL DIO
messages.

Cooja logs are converted into 60-second routing windows. Features include
application traffic, radio activity, RPL control-message counts, rank
observations, parent switching and topology summaries. Attack-specific debug
markers are preserved for validation but excluded from IDS training to avoid
leakage.

The static drift experiment trains on one attack/control family and tests on a
different attack/control family. This is treated as controlled
attack-distribution drift: the simulation platform and feature pipeline are
held fixed while the attack mechanism changes. The adaptation experiment then
adds zero, one, two or three whole target-family seeds to the source training
data and evaluates only on held-out target seeds. This whole-seed split avoids
overstating performance through random row leakage.

The supplied Gope/professor dataset is used separately as an external baseline.
It validates that the IDS pipeline can reproduce strong supervised performance
on existing 6LoWPAN/RPL data. It is not merged with the Cooja campaign, because
the Cooja experiments provide the controlled drift, adaptation and Sybil
evidence.

## 3. Implementation

The implementation is organised around experiment packages. Attack
implementations, generated configurations, validation summaries and analysis
outputs are stored under `experiments/`. Key packages include the preserved
blackhole and sinkhole runs, additional attack implementations, Sybil attack
evidence, cross-attack drift results, adaptation curves, trust diagnostics,
external dataset reproduction and dissertation result summaries.

The attacks follow a shared delayed-activation pattern. Attack applications log
their startup state, run normally at first and activate malicious behaviour
after 240 seconds. Matched control applications keep the corresponding attack
flag disabled. This gives a consistent experimental design across attack
families.

Sybil is implemented as the new attack surface. A weak Contiki hook keeps the
attack disabled by default. The Sybil attack application enables rotating
virtual IPv6 source identities for outgoing RPL DIO messages. The real mote and
RPL state remain intact; the manipulated surface is the identity observed by
neighbouring nodes.

Validation scripts check run completion, seed matching, expected attack
activation and absence of attack markers in control runs. Sybil attack runs
produced 150-151 spoofed DIO identity events each, while matched controls
produced zero Sybil activation or spoofing markers.

The trust layer is implemented offline. It derives forwarding, rank, control
and route trust scores from existing routing-window features. This layer is
used diagnostically to explain which attack surface is suspicious. It does not
currently alter RPL parent selection and should not be claimed as a complete
defence.

## 4. Results

Nine attack families were validated in Cooja, each with five attack runs and
five matched control runs. This gives 90 validated runs and supports a broader
evaluation than a single-attack IDS experiment.

The static cross-attack experiment shows poor generalisation. For the CART
model, 48 of 72 cross-attack train/test pairs had zero attack recall and only
six reached F1 greater than or equal to 0.8. The Gaussian model performed worse:
66 of 72 pairs had zero recall and no pair reached F1 greater than or equal to
0.8. This shows that the key failure is not just reduced accuracy, but complete
missed detection in many changed attack environments.

The external Gope/professor dataset supports baseline credibility. Under the
temporal/source-order split, the Random Forest top-six baseline achieved mean
accuracy 99.63%, mean recall 98.57%, mean F1 98.08% and mean FPR 0.0043 across
eight attack families. This confirms that the pipeline can reproduce strong
static supervised classification on existing data, while the Cooja campaign
tests controlled drift and adaptation.

Adaptation improved performance substantially. With no target adaptation seeds,
mean CART recall was 0.2333 and mean F1 was 0.1822. With one whole target seed,
mean recall increased to 0.8056 and mean F1 to 0.8258. With two target seeds,
mean F1 reached 0.8664; with three, it reached 0.8792.

The focused blackhole-to-sinkhole experiment also distinguishes two operational
signals of change. A label-free CUSUM over persistent low-rank RPL state detected
all five sinkhole activations at the first 60-second post-activation window,
with no observed alarm in the five matched controls. DDM over delayed errors
from the static CART IDS detected the same five runs one window later, because
the monitored prediction errors are not available until their labels arrive.
This is a controlled comparison of different evidence sources, not a general
claim that one detector is universally superior.

Sybil provides the clearest new attack-surface result. Static CART models
involving Sybil produced 11 zero-recall failures out of 16 Sybil-related
cross-attack pairs. When Sybil was the target family, mean F1 was 0.2183 with no
Sybil adaptation data and 0.9683 with one whole Sybil adaptation seed.

The trust layer did not improve CART metrics over the existing routing-feature
baseline. This is a useful negative result. Trust scores derived from existing
features improve interpretability, but they do not automatically add predictive
information unless they capture new evidence or influence routing decisions
online.

## 5. Discussion

The central finding is that attack evolution changes the feature distribution
seen by the IDS. Static models trained on one attack mechanism often fail when
the test attack affects a different part of the RPL protocol. This should be
described as controlled attack-distribution drift rather than naturally
observed deployment drift.

The adaptation results show partial recovery. Whole-seed target adaptation is a
more defensible design than random row splitting because evaluation windows
come from simulations not used for adaptation. The curve also answers a useful
operational question: how much target-environment evidence is needed before the
IDS begins to recover?

The results also show why adaptation is not enough by itself. If the feature
representation does not expose the changed attack mechanism, retraining can
fail or produce weak improvements. This is the important interpretation of the
sinkhole and trust-layer concerns: feature design and model updating have to be
considered together.

Sybil strengthens the originality of the project because it shifts the attack
surface from forwarding, rank, route choice or topology manipulation to
identity-related control-plane behaviour. The dissertation should claim that
this is an implemented and evaluated Sybil-style identity-manipulation
experiment in Cooja/RPL-lite, not that it proves cryptographic compromise or
solves Sybil defence.

The trust layer should be presented as diagnostic. Forwarding trust is well
matched to blackhole and grayhole behaviour, while rank, control and route
trust expose other mechanisms to different degrees. Wormhole and Sybil remain
harder because reliable forwarding or fresh identities can undermine simple
trust assumptions.

## 6. Limitations

The study uses Cooja rather than a physical 6LoWPAN testbed. This supports
control and reproducibility but does not capture every radio, hardware,
mobility or environmental factor present in real deployments.

Each attack family has five attack seeds and five matched control seeds. This
is suitable for a controlled MSc-level experiment, but not enough to claim
general deployment robustness. For example, an observed five out of five
detector success rate still has a Wilson 95% lower bound of 0.5655; small-run
uncertainty must be reported alongside the point estimate.

The attack set is broad but incomplete. Version-number attacks, collusion,
mobile attackers and cryptographic identity compromise are not fully evaluated.

The IDS depends on extracted routing-window features. If those features do not
make the changed attack mechanism visible, adaptation may not recover
performance. This is a central limitation and also one of the dissertation's
main findings.

The trust layer is offline and diagnostic. It does not currently prevent
malicious routing choices or modify RPL parent selection.

The LLM explanation layer, if used, depends on structured evidence created by
the pipeline. It should not infer hidden facts, prove attacker identity or be
reported as the detector.

The adaptation workflow models recovery after representative target-family
labels become available. It does not autonomously retrain a deployed Contiki
node, and it does not implement the full adversarial-RL and incremental model
selection architecture of the motivating NetSim study.

## 7. Conclusion

This dissertation implemented and evaluated an RPL/6LoWPAN IDS workflow under
controlled attack-distribution change. Nine attack families were validated in
Contiki-NG/Cooja, producing 90 validated simulation runs. The work reproduced
multiple established RPL attack behaviours and added Sybil identity
manipulation as a new attack surface.

The main finding is that static IDS models are brittle under cross-attack
concept drift. The CART model produced zero attack recall in 48 of 72
cross-attack pairs. This demonstrates that strong supervised performance on one
attack environment does not guarantee detection when the attack mechanism
changes.

Whole-seed adaptation substantially recovered performance. Mean CART F1
increased from 0.1822 with no target-family seeds to 0.8258 with one target
seed and 0.8792 with three target seeds. Sybil was a strong example of this
effect: static Sybil-target F1 was 0.2183, while one Sybil adaptation seed
raised held-out F1 to 0.9683.

Overall, the project shows that RPL IDS evaluation should consider not only
static detection accuracy, but also generalisation under changing attack
behaviour, recovery through adaptation and whether the feature representation
captures the changed attack mechanism.

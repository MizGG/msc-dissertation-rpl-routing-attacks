# Methodology

## Research Design

This study evaluates whether an RPL intrusion detection system remains reliable
when the attack mechanism changes. The central experiment is controlled
cross-attack distribution shift: an IDS trained on labelled control and attack
data from one RPL attack family is evaluated on a different family. Contiki-NG
and Cooja provide repeatable activation, known ground truth, matched controls,
and routing telemetry. Results are controlled simulation evidence, not physical
testbed or production-deployment claims.

## Simulation and Dataset

Nine families were evaluated: blackhole, sinkhole, DIS flooding, grayhole,
increase-rank, DIO suppression, worst-parent, wormhole, and Sybil. Every family
has five attack and five matched control seeds, giving 90 validated baseline
runs. Attacks activate at 240 s in a 540 s simulation.

Raw logs are converted into 60-second routing windows. The frozen baseline
dataset contains 810 windows across 90 complete `family:mode:seed` groups.
Features include application traffic, radio events, RPL control traffic, DIO
rank observations, parent changes, and inferred topology. Simulator attack
markers are retained for validation only and excluded from IDS and drift inputs.

## Evaluation Protocol

The unit of independence is one complete Cooja run. All windows from a
`family:mode:seed` group remain in one partition; random row splitting is not
used. Gaussian and CART classifiers are evaluated with accuracy, precision,
attack recall, F1, false-positive rate, and confusion matrices.

Cross-attack testing trains on one family and tests on another. It is described
as a controlled attack-distribution change used to evaluate concept drift, not
as natural drift observed in a deployed network. Adaptation adds zero, one,
two, or three complete target-family seed groups and evaluates only on unseen
target seeds.

## Online Drift, Robustness and Defence

Chronological windows are used for rank-state CUSUM and delayed-error DDM
evaluation against the known 240 s boundary and matched controls. Robustness is
evaluated separately with attacker relocation and lossy-radio conditions; these
60 extra runs are not merged into the baseline corpus. A separate 15-run
sinkhole-defence campaign measures application responses, misses, parent
changes, and Cooja radio-event counts for a rank-parent intervention.

The supplied Gope data are separate supporting baseline evidence. They are not
merged with Cooja observations or treated as directly interchangeable.

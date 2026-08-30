# Results

## Dataset and Attack Validation

The primary simulated dataset contains 810 labelled 60-second windows from 90
validated Cooja runs, covering nine attack families. The audit found no empty
values, non-numeric features, duplicate windows, or incomplete sequences. It
excludes 16 explicit attack-marker fields and leaves 57 generic numeric features
eligible before model-specific selection.

## Static Cross-Attack Drift

The CART cross-attack evaluation contains 72 source-target pairs. Forty-eight
pairs produced zero attack recall and mean cross-attack F1 was 0.1823. The
Gaussian model was weaker: 66 of 72 pairs produced zero recall. This shows poor
transfer after a controlled change in attack mechanism, rather than proving
naturally occurring real-world drift.

## Adaptation and Sybil

Whole-seed adaptation increased mean CART F1 from 0.1822 with no target data to
0.8258 with one target seed, 0.8664 with two seeds, and 0.8792 with three. Test
seeds were never used for adaptation. Sybil provides the new identity-related
attack surface: 11 of 16 Sybil-related static pairs had zero recall. When Sybil
was the target, mean F1 rose from 0.2183 without adaptation to 0.9683 after one
complete Sybil adaptation seed.

## Online Drift and Robustness

Both monitors detected all five held-out sinkhole attacks and produced no false
alert on five matched controls. Rank-state CUSUM alerted in the first
post-activation 60-second window; delayed-error DDM alerted 60 s later.

Static results were condition-sensitive. Under attacker relocation, coarse plus
routing CART F1 was 0.4762 for blackhole and Sybil and 0.4950 for sinkhole;
three complete target-condition seeds raised these to 1.0000, 0.9947, and
1.0000 respectively. Under lossy radio, three-seed adaptation produced F1 of
1.0000 for blackhole and sinkhole and 0.9367 for Sybil. These are Cooja
condition-specific results, not universal deployment claims.

## Sinkhole Defence Prototype

The unmitigated sinkhole had near-control application responses in this
topology, 416.6 versus 417.4, but distinct low-rank telemetry. The rank-parent
prototype was harmful: responses fell to 87.4, with 28.8 missed responses and
681.8 parent switches per run. Mean radio events increased from 5,217.4 in
control to 35,020.0 with defence, a 571.22% increase. The intervention is not
claimed as a successful mitigation.

## Supporting External Baseline

The supplied Gope data are reported separately. The temporal/source-order
Random Forest top-six baseline achieved mean accuracy 99.63%, recall 98.57%, F1
98.08%, and false-positive rate 0.0043 across eight attack files. This supports
pipeline reproducibility, not the Cooja drift or Sybil conclusions.

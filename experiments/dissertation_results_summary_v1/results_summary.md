# Dissertation Results Summary

This folder collects the main dissertation-facing evidence from the Cooja and
IDS experiments. It is intended as a compact source for the results chapter,
methodology chapter and supervisor updates.

## What Has Been Completed

Nine RPL attack families have been implemented, run and validated in Cooja:

- blackhole;
- sinkhole;
- DIS flood;
- grayhole;
- increase-rank;
- DIO suppression;
- worst-parent;
- wormhole;
- Sybil.

Each attack family has five attack runs and five matched control runs. The main
validated attack set therefore contains 90 Cooja runs. The first eight attack
families support reproduction and extension of the existing RPL attack work. The
Sybil family is the new attack-surface contribution.

## Concept Drift Result

The concept-drift experiment treats each attack family as a different operating
environment. IDS models are trained on one attack/control family and tested on a
different attack/control family using 60-second routing windows.

With Sybil included, the nine-family static CART matrix contains 72
cross-attack train/test pairs. Of these, 48 have zero attack recall and only 6
reach F1 >= 0.8. This shows that static IDS performance often collapses when
the attack behaviour changes.

The Gaussian model is weaker under this setting: 66 of 72 cross-attack pairs
have zero recall and no cross-attack pair reaches F1 >= 0.8.

## Adaptation Result

The adaptation experiment adds 0-3 whole target-family simulation seeds to the
source-family training data, then evaluates only on held-out target seeds. The
split is by whole Cooja seed, not random rows.

Overall CART performance improves substantially:

- 0 target seeds: mean recall 0.2333, mean F1 0.1822.
- 1 target seed: mean recall 0.8056, mean F1 0.8258.
- 2 target seeds: mean recall 0.8620, mean F1 0.8664.
- 3 target seeds: mean recall 0.8917, mean F1 0.8792.

This supports the dissertation claim that limited target-environment data can
recover IDS performance after attack-distribution drift.

## Sybil/New Attack-Surface Result

Sybil manipulates the RPL identity surface by rotating the IPv6 source identity
used for outgoing RPL DIO messages. This is distinct from forwarding attacks,
rank manipulation, DIO suppression, DIS flooding, parent-choice manipulation
and wormhole tunnelling.

Static CART models involving Sybil have 11 zero-recall failures out of 16
Sybil-related cross-attack pairs. When Sybil is the target attack family, mean
F1 improves from 0.2183 with no Sybil adaptation data to 0.9683 with one whole
Sybil adaptation seed.

## Defensible Interpretation

The strongest interpretation is not simply that retraining improves a model.
The defensible contribution is that attack evolution changes the feature
distribution seen by the IDS. Some attack families transfer poorly because the
features learned from one mechanism do not expose the changed mechanism in
another. Adaptation helps when the new target behaviour is represented by whole
simulation runs.

This also explains earlier weaker sinkhole results: if the current coarse
routing-window features do not expose the attack mechanism strongly enough,
adaptation alone may not solve the problem. Feature representation and
adaptation must be considered together.

## Evidence Files

- Attack coverage table: `attack_coverage_table.csv`
- Static drift metrics: `concept_drift_key_metrics.csv`
- Adaptation metrics: `adaptation_key_metrics.csv`
- Sybil contribution note: `sybil_contribution_summary.md`
- Full Sybil drift matrix: `experiments/cross_attack_drift_with_sybil_v1/results/cross_attack_matrix.csv`
- Full Sybil adaptation curves: `experiments/cross_attack_adaptation_with_sybil_v1/cross_attack_adaptation_curves.csv`

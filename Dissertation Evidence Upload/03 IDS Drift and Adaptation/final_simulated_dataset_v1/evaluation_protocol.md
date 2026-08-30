# Whole-Seed Evaluation Protocol

The unit of independence is a complete Cooja simulation run, identified by
`family:mode:seed`. All nine 60-second windows from that group must remain in
the same partition.

## In-Domain Evaluation

For a family, choose whole attack and control seed groups for training and hold
out different attack and control seed groups for testing. Report accuracy,
precision, recall, F1, false-positive rate, and a confusion matrix.

## Cross-Attack Drift

Train using control and attack groups from source family A. Test only on
control and attack groups from target family B. Do not claim that the test is
in-domain performance; it measures controlled cross-attack distribution shift.

## Adaptation

Add one or more complete target-family seed groups to the original training
set. Evaluate only on target-family seed groups that were not used during
adaptation. Report the number of target seeds used and all standard metrics.

## Online Drift

Keep each run's windows in chronological order. Fit the reference distribution
without the matching target seed, then evaluate alerts relative to the known
240-second activation boundary. Report detection delay and matched-control
false alarms.

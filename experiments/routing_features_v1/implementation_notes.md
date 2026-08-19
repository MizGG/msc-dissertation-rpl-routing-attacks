# Routing-Feature Implementation Notes

## Controlled Change

The validated blackhole and sinkhole Cooja topologies, seeds, positions,
traffic, 240-second activation and 540-second duration are unchanged. The
preserved final evidence folders were not modified.

The routing-feature configs set `LOG_CONF_LEVEL_RPL=LOG_LEVEL_INFO`. This
enables Contiki-NG's existing generic telemetry for received and transmitted
DIO rank, DIS/DAO counts, parent switches, internal rank, neighbor counts and
root routing-table snapshots. No attack-specific telemetry field is used by
the classifiers.

## Weak-Flag Correction

The generic telemetry exposed that the original weak-only sinkhole flag
produced one rank-128 advertisement at activation, after which node 16 reverted
to rank 256. Cooja loads mote firmware as shared libraries, allowing weak-symbol
interposition between mote types.

The routing experiment therefore gives both sinkhole router firmwares a strong
`sinkhole_attack_enabled` definition. The RPL hook remains unchanged and still
preserves internal rank. Diagnostic weak-flag runs are retained separately in
`experiments/routing_features_weak_flag_diagnostic/`.

## Feature and Leakage Controls

Each run is divided into nine 60-second windows. Attack-run windows before 240
seconds remain normal; windows from 240 seconds onward are attack. Adaptation
and evaluation are split by complete seed.

The stateful extractor retains the latest generic DIO rank per receiver/sender
pair, matching a central routing IDS that maintains topology state. It derives
low-rank non-root sender counts and receiver exposure without reading the
`SINKHOLE` log marker. Explicit sinkhole/blackhole activation and drop fields
remain in the CSV only for evidence validation and are excluded from every
feature set.

The ablation compares the same classifier using coarse traffic/radio features
and coarse plus routing-state features. Gaussian Naive Bayes and a deterministic
depth-limited CART classifier are both reported.

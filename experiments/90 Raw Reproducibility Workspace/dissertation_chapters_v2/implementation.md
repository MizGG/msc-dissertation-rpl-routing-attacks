# Implementation

The implementation contains Cooja attack/control applications, small RPL-lite
hooks where required, per-experiment Cooja configurations, and local Python
standard-library scripts for validation and feature extraction. No network
service, API key, cloud component, or AI component is required to reproduce the
Cooja campaign or frozen dataset.

Blackhole and grayhole modify forwarding behaviour; sinkhole advertises a low
rank while retaining the node's internal rank; DIS flood, increase-rank, DIO
suppression, worst-parent, and wormhole modify their corresponding RPL
behaviours. Sybil emits RPL DIO messages with rotating virtual identities after
the common activation time. It is a Sybil-style identity-manipulation scenario
in Cooja/RPL-lite, not cryptographic identity compromise.

The sinkhole defence is isolated from all baseline campaigns. Its
disabled-by-default neighbour-selection hook is enabled only by a dedicated
defence client. This preserves established evidence while allowing a
reproducible test of the rank-parent intervention.

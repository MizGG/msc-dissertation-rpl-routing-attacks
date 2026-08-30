# Sybil Rate Campaign Notes

## Question

Does the isolated Sybil implementation produce reproducibly distinct spoofed-DIO
rates while preserving the same 240-second activation boundary and Cooja setup?

## Design

The campaign uses five fixed seeds. Node 16 is the only altered mote. It sends
spoofed multicast RPL DIO messages after 240 seconds at either 10-second
(`low`) or 1-second (`high`) intervals. A normal-RPL control is run once per
seed and shared by both rate comparisons. This avoids treating duplicate normal
simulations as independent evidence.

## Validation Rule

Every run must have a Cooja completion marker, radio log, one startup marker,
and, for attacks, one activation marker plus at least one spoofed-DIO marker.
The campaign validator reports 15/15 valid runs.

## Evidence Boundary

The low-rate and high-rate marker counts demonstrate that the intended source
behaviour executed in Cooja. Radio metrics quantify simulator transmissions,
not physical packet delivery, energy use, or a defence success rate. This
campaign is an attack-intensity sensitivity extension. It does not establish
that the existing IDS detects either rate, and it does not itself implement a
Sybil defence.

## Next Defensible Step

Use the saved logs to define an identity-consistency feature (for example,
unexpected DIO source-identity churn or inconsistent DIO rate per claimed
identity), then evaluate it on held-out seeds before allowing it to affect RPL
parent selection. A forwarding-trust score alone is not a sufficient Sybil
defence because a sender can behave as a normal forwarder while emitting
multiple identities.

The package-local `project-conf.h` enables the existing IPv6 warning that
prints each virtual source identity. A fresh, separately stored smoke run must
confirm the log is visible before this evidence is used for an identity feature.

The separate five-seed identity-observable campaign has now confirmed this
condition. `evaluate_identity_consistency.py` uses only the emitted virtual
address records to calculate observation count, number of distinct addresses,
and identity-churn events. It is an offline evidence feature, not yet an RPL
enforcement mechanism.

The virtual-identity observation count can exceed the rate application's
scheduled spoofed-DIO count. This is expected: once enabled, the existing hook
rewrites the source address of both the application's DIOs and any naturally
scheduled RPL DIOs sent by node 16. The validator therefore requires at least
the scheduled count, rather than incorrectly asserting equality.

`evaluate_sybil_identity_monitor.py` converts virtual-address observations into
a simple 60-second alert: any `fd00::fxxx` identity is inconsistent with the
controlled address plan used by this topology. This is intentionally a
transparent offline monitor rather than a trained classifier. Its result is
valid only for this controlled address allocation and cannot yet be claimed as
a general Sybil defence or a routing-layer mitigation.

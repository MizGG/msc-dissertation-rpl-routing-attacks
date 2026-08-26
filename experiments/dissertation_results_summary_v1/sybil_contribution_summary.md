# Sybil Contribution Summary

The Sybil workstream adds a new RPL attack surface beyond the reproduced attack
families. Instead of dropping packets, changing rank, suppressing DIOs, flooding
DIS messages, forcing parent choices or creating a wormhole tunnel, the attacker
manipulates identity. A single malicious mote sends RPL DIO messages using
rotating virtual IPv6 source identities.

## Implementation

- Attacker application: `experiments/sybil_attack_v1/code/sybil-router.c`
- Control application: `experiments/sybil_attack_v1/code/sybil-control-router.c`
- Contiki hook snapshot: `experiments/sybil_attack_v1/contiki_snapshots/uip-icmp6.c`
- Patch file: `experiments/sybil_attack_v1/code/uip-icmp6-sybil-hook.patch`
- Cooja configurations: `experiments/sybil_attack_v1/configs/`

The hook uses a weak `sybil_attack_enabled` flag. The control app keeps this
flag disabled. The attack app enables it after 240 seconds and then sends
periodic multicast DIOs, which are emitted with rotating source identities.

## Validation

Five attack and five matched control Cooja runs were completed. All validated
successfully.

- Attack runs: 150-151 spoofed DIO identity events per run.
- Control runs: zero Sybil activation or spoofing markers.
- Validation file: `experiments/sybil_attack_v1/validation_summary.csv`

## Concept Drift Role

Sybil was included in the nine-family cross-attack concept-drift experiment.
Static CART models involving Sybil produced 11 zero-recall failures out of 16
Sybil-related cross-attack pairs. This supports the argument that a static IDS
trained on one RPL attack surface may not generalise to a newly introduced
identity-manipulation attack.

## Adaptation Role

When Sybil is the target family, static performance is poor:

- 0 Sybil adaptation seeds: mean F1 = 0.2183.

Adding limited Sybil data restores detection:

- 1 Sybil adaptation seed: mean F1 = 0.9683.
- 2 Sybil adaptation seeds: mean F1 = 0.9616.
- 3 Sybil adaptation seeds: mean F1 = 0.9688.

This is a strong dissertation result because it connects the new attack surface
directly to the concept-drift question: the IDS fails under changed attack
behaviour, then recovers when representative examples of the new behaviour are
introduced.

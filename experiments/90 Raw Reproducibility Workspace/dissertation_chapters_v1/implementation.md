# Implementation

## Repository Structure

The implementation is organised around experiment packages. Each package
contains source code, generated Cooja configurations, validation outputs and
results needed to reproduce the corresponding claim.

Key evidence folders:

- `experiments/blackhole/final_corrected_240s_540s`
- `experiments/sinkhole/final_corrected_240s_540s`
- `experiments/additional_attacks_v1`
- `experiments/sybil_attack_v1`
- `experiments/cross_attack_drift_with_sybil_v1`
- `experiments/cross_attack_adaptation_with_sybil_v1`
- `experiments/trust_layer_v1`
- `experiments/llm_explanations_v2`
- `experiments/dissertation_results_summary_v1`

## Attack Implementations

The attack applications follow a shared pattern. Each attack starts disabled,
logs its startup state, waits until 240 seconds and then enables the malicious
behaviour. Matched control applications keep the corresponding attack flag
disabled.

Blackhole and grayhole attacks manipulate forwarding behaviour. DIS flood and
DIO suppression manipulate RPL control-message behaviour. Sinkhole and
increase-rank manipulate advertised rank. Worst-parent manipulates parent
selection. Wormhole introduces a radio/topology shortcut. Sybil manipulates the
source identity used for RPL DIO messages.

## Sybil New Attack Surface

Sybil is implemented using a weak Contiki hook in `uip-icmp6.c`. The default
weak variable keeps the attack disabled unless an experiment application
overrides it. Once enabled, outgoing RPL DIO messages are sent using rotating
virtual IPv6 source identities. The real mote and RPL state remain intact; the
manipulated surface is the identity observed by neighbours.

Five attack and five matched control Sybil runs were completed. Attack runs
produced 150-151 spoofed DIO identity events each, while controls produced zero
Sybil activation or spoofing markers.

## Validation

Validation scripts check that runs completed, seeds match, attacks activate only
in attack configurations and controls remain free of attack markers. The main
attack evidence contains 90 validated Cooja runs across nine families.

## Feature Pipeline

The routing-window feature extractor parses Cooja logs into 60-second windows.
It records traffic, radio, RPL control-plane, rank, parent and topology
features. Attack-specific markers are preserved for audit and validation but
excluded from primary IDS features.

The Sybil update added support for `SYBIL_*` run identifiers and Sybil marker
columns. The cross-attack scripts were also updated so Sybil marker fields are
excluded from the model feature set by default.

## Trust Layer

The trust layer is implemented offline in `experiments/trust_layer_v1`. It
derives trust scores from existing features:

- forwarding trust from application response and missed-packet behaviour;
- rank trust from low-rank non-root observations;
- control trust from abnormal DIS/DIO/DAO and DIO sender behaviour;
- route trust from parent switching and topology instability.

The layer also emits interpretable alert flags. It does not currently change
RPL parent selection.

## LLM Layer

The LLM layer is implemented in `experiments/llm_explanations_v2`. The builder
script creates one explanation case for each attack family using structured
evidence from the trust-enhanced feature CSV and cross-attack/adaptation result
files. The scorer evaluates JSON explanations against hidden rubrics.

The package includes a handcrafted fixture to test schema and scoring. This
fixture is not live LLM performance and should not be reported as such.


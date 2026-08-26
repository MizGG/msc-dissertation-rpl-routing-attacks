# Limitations

## Simulation Scope

The experiments use Cooja simulations rather than a physical 6LoWPAN testbed.
This gives control and reproducibility but may not capture all radio, hardware,
mobility and environmental effects present in real deployments.

## Dataset Size

Each attack family has five attack seeds and five matched control seeds. This is
enough for a controlled MSc-level experimental study, but not enough to claim
general deployment robustness. Results should be interpreted as evidence from a
controlled simulation campaign.

## Attack Coverage

Nine attack families are included, but the study does not cover every possible
RPL or IoT attack. Version-number attacks, collusion, mobile attackers and
cryptographic identity compromise are not fully evaluated.

## Feature Representation

The IDS depends on extracted routing-window features. If an attack mechanism is
not visible in those features, model adaptation may fail or appear weaker than
the true attack impact. This was a key concern for some subtle attacks.

## Trust Layer

The trust layer is offline and diagnostic. It does not currently alter RPL
parent selection or prevent malicious routing choices. It is useful for
interpretation but should not be reported as a complete defence.

## LLM Layer

The LLM explanation layer depends on structured evidence created by the
pipeline. If the evidence is incomplete, the explanation may be incomplete.
The LLM should not be used to infer hidden facts from raw logs or to prove
attacker identity. Any live LLM evaluation must report model version, prompt
settings, raw outputs and unsupported-claim rate.

## Generalisation

The cross-attack experiment evaluates attack-family transfer, not all forms of
real-world concept drift. Changes in topology size, traffic workload, radio
conditions, mobility or deployment environment could create additional drift
not fully captured here.


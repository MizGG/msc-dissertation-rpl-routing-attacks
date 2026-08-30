# Methodology Comparison and Bounded Claims

## What This Dissertation Implements

The dissertation uses Contiki-NG/Cooja to run deployable Contiki firmware in a
controlled 16-node RPL network. Nine attack families have five attack and five
matched control runs, with attack activation at 240 seconds in a 540-second
simulation. The IDS analysis uses 60-second routing windows, cross-attack
evaluation, complete-seed separation for adaptation, an offline trust
diagnostic, and two monitored blackhole-to-sinkhole change signals.

## Comparison With the Adversarial RL Paper

The Gope/Pasikhani paper uses NetSim, 16-128 nodes, mobility, multiple
topologies, approximately 240-minute simulations, attack profiles, DDM and
other drift-detector comparisons, incremental KNNADWIN and DQN/DDQN defender
models, and adversarial reinforcement learning.

This dissertation does not reproduce that complete architecture. Its controlled
cross-attack transfer design is an independent extension: a model trained on
one RPL attack family is evaluated on a changed attack family, and adaptation
uses only whole target-family Cooja seeds that are excluded from held-out
evaluation. The CUSUM monitor and target-seed adaptation are original project
components inspired by the same evolving-data problem, not implementations of
the paper's adversarial RL method.

## Comparison With SVELTE

SVELTE used Contiki/Cooja and emulated Tmote Sky nodes, then implemented an
online 6BR-based 6Mapper that reconstructs routing state to detect sinkhole and
selective forwarding. It evaluated detection as well as energy and memory
overhead.

This dissertation similarly benefits from Cooja's deployable firmware model,
but it does not implement a 6Mapper or a deployed prevention mechanism. Its
contribution is broader attack-family coverage and evidence that static
cross-attack IDS transfer fails. The offline trust scores are diagnostic only;
they must not be presented as an online defence.

## Simulation Rather Than Physical Deployment

The experiments are simulations/emulations, not a physical IoT deployment.
Cooja supports reproducibility, controlled seeds and execution of Contiki-NG
firmware, but it cannot reproduce every radio, hardware, interference, power
and mobility effect of a field testbed. The correct claim is therefore:

> The results provide controlled Cooja evidence, not a field-deployment
> guarantee.

## Current Validity Boundaries

- Five attack and five control seeds per family are adequate for a controlled
  proof of concept but produce wide run-level uncertainty intervals.
- The primary topology is a fixed 16-node configuration; no scalability or
  mobility claim is made.
- CUSUM is designed for persistent low-rank RPL state in the blackhole-to-
  sinkhole experiment. It is not a universal drift detector.
- DDM requires delayed labels because it monitors prediction error; CUSUM does
  not use labels or attack markers as inputs.
- Whole-seed adaptation is an offline approximation of recovery after target
  labels become available. Autonomous in-network retraining is future work.
- No energy, ROM/RAM, latency or physical-testbed result is claimed for the
  current IDS/trust layers.

## Highest-Value Next Cooja Campaign

Run only Blackhole, Sinkhole and Sybil under two additional conditions: one
changed layout and one higher-loss radio setting. Keep five seeds per condition,
then repeat the static transfer, CUSUM/DDM, and whole-seed adaptation analysis.
This tests sensitivity without multiplying the complete nine-attack campaign.

## Future Online Trust Defence

A narrow, defensible follow-up is a sinkhole rank/parent consistency guard:

1. observe advertised rank and parent relationship;
2. penalise persistent non-root low-rank inconsistency;
3. prevent the suspicious candidate becoming preferred parent;
4. compare attack delivery, route choice, false alarms and radio overhead with
   matched controls.

It should be introduced as a new experiment, not retrospectively claimed for
the current offline trust results.

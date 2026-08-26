# Five-Minute Demo Script

## 0:00-0:40: Setup

This project evaluates IDS robustness in RPL/6LoWPAN networks when attack
behaviour changes. I use Contiki-NG and Cooja to run controlled RPL attacks,
then evaluate static IDS transfer, adaptation, trust diagnostics and an
evidence-grounded LLM explanation layer.

## 0:40-1:20: Cooja Evidence

Show the Sybil Cooja config and validation summary.

Say:

The simulation uses delayed attack activation at 240 seconds. For Sybil, the
attacker manipulates the RPL identity surface by sending DIO messages from
rotating virtual IPv6 source identities. Across five attack seeds this produced
150-151 spoofed identity events per run, while matched controls produced zero.

## 1:20-2:10: Attack Coverage

Show `attack_coverage_table.csv`.

Say:

There are nine validated attack families, each with five attack runs and five
matched controls. The first eight support reproduction and extension of known
RPL attack families. Sybil is the new attack surface.

## 2:10-3:00: Concept Drift

Show `static_drift_zero_recall.svg` or `concept_drift_key_metrics.csv`.

Say:

The key question is whether a static IDS trained on one attack family
generalises to another. In the nine-family CART matrix, 48 of 72 cross-attack
pairs had zero attack recall. This means the model often missed the attack
after the attack mechanism changed.

## 3:00-3:40: Adaptation

Show `overall_adaptation_curve.svg`.

Say:

When limited target-family data is added using whole simulation seeds,
performance recovers. Mean F1 rises from 0.1822 with no target data to 0.8258
with one target seed and 0.8792 with three target seeds.

## 3:40-4:20: LLM Explanation Layer

Run or show the LLM package.

Say:

The LLM is not the IDS. It receives structured IDS, drift, adaptation and trust
evidence and produces a constrained explanation. The evaluation checks
faithfulness, mechanism alignment, uncertainty, drift awareness, actionability
and unsupported claims.

## 4:20-5:00: Closing

Say:

The main contribution is not just implementing attacks. The work shows that IDS
performance can collapse under controlled attack-distribution drift, that
whole-seed adaptation can recover performance, and that Sybil introduces a new
identity-manipulation surface. The trust and LLM layers support interpretation
without overclaiming detection.


# Methodology

## Overview

This project evaluates how an intrusion detection system for RPL/6LoWPAN
networks behaves when the attack environment changes. The core methodology is a
controlled concept-drift experiment: models are trained on one RPL attack family
and evaluated on another. The work combines Contiki-NG/Cooja simulation,
feature extraction, static IDS evaluation, adaptation experiments, trust-aware
diagnostics and an evidence-grounded LLM explanation layer.

The LLM is not used as the detector. Detection and drift evidence are produced
first by the IDS, feature pipeline, adaptation experiment and trust diagnostics.
The LLM receives structured evidence and produces a human-readable explanation.

The main methodological claim is therefore not that one classifier achieves
high accuracy on a single fixed dataset. The study instead asks whether an IDS
trained on one RPL attack mechanism remains reliable when the attack mechanism
changes, and whether limited whole-run adaptation data can recover detection
performance without leaking test windows from the same simulation run.

## Simulation Environment

The network experiments were run in Contiki-NG using Cooja. RPL-lite was used
as the routing stack. Each attack family was evaluated with matched attack and
control configurations. The main validated Cooja set contains nine attack
families, each with five attack seeds and five matched control seeds, giving 90
validated Cooja runs.

All attacks use a delayed activation design. Attack applications begin in a
disabled state and activate after 240 seconds. This creates a pre-attack
baseline period and a post-activation attack period in the same simulation run.
The total simulation duration is 540 seconds, allowing five 60-second
post-activation windows.

## Attack Families

The reproduced and extended RPL attack families are:

- blackhole;
- sinkhole;
- DIS flood;
- grayhole;
- increase-rank;
- DIO suppression;
- worst-parent;
- wormhole;
- Sybil.

The first eight families support reproduction and extension of existing RPL
attack work. Sybil is treated as the new attack-surface contribution because it
manipulates identity rather than forwarding behaviour, rank, control-message
timing, parent choice or topology tunnelling.

The attack set was deliberately kept mechanism-diverse. Blackhole and grayhole
primarily affect forwarding behaviour; sinkhole and increase-rank alter routing
rank incentives; DIS flood and DIO suppression alter control-plane dynamics;
worst-parent changes route selection; wormhole changes topology plausibility;
and Sybil changes the identity surface visible through RPL DIO messages. This
diversity is what makes the cross-attack experiment a meaningful controlled
drift test rather than a same-distribution train/test split.

## Feature Extraction

Cooja logs are converted into 60-second routing windows. Each window includes
application traffic counts, radio activity, RPL control-message counts, rank
observations, parent-switching behaviour, topology summaries and attack-marker
fields used only for validation.

The primary IDS feature set excludes simulator attack-marker fields such as
activation messages and attack-specific log strings. This avoids a leakage
problem where the classifier could learn debug instrumentation rather than
network behaviour.

## IDS and Concept Drift Evaluation

The static drift experiment trains a model on one attack/control family and
tests it on another. This treats each attack family as a different operating
environment. A failure to transfer, especially zero attack recall, is interpreted
as evidence that the static IDS does not generalise to the changed attack
mechanism.

This is framed as induced or controlled concept drift. The independent variable
is the attack family used at test time, while the simulation platform, windowing
method and feature extraction pipeline are kept fixed. This isolates the effect
of attack-mechanism change more clearly than a mixed random split, where windows
from related runs can make the problem appear easier than it would be in a
changed deployment.

Two simple models are evaluated: a Gaussian classifier and a CART-style decision
tree. The CART model is the main reported model because it is interpretable and
performed more strongly in the cross-attack setting.

## External Dataset Baseline

The supplied Gope/professor dataset is used as an external static baseline. It
is not merged with the Cooja simulations. Instead, it checks that the IDS
pipeline can reproduce strong supervised classification performance on existing
6LoWPAN/RPL attack data. The Cooja experiments then provide the controlled
concept-drift, adaptation and Sybil new-attack evidence.

The external baseline uses random and temporal/source-order splits over the
supplied CSV files. The temporal/source-order split is the more conservative
summary because it avoids relying only on random row mixing.

## Adaptation Evaluation

The adaptation experiment evaluates whether limited examples from the new attack
environment can recover performance. The model is trained on a source
attack/control family and then supplemented with zero, one, two or three whole
target-family seeds. Evaluation is performed only on target seeds not used for
adaptation.

Splitting by whole simulation seed is important. Random row-level splitting
would leak highly related windows from the same simulation into both training
and evaluation and would overstate adaptation performance.

The adaptation curve is used instead of a single retraining result because it
answers a more useful operational question: how much target-environment
evidence is required before the IDS begins to recover from the distribution
change? Reporting zero, one, two and three target-seed conditions also exposes
failure cases where retraining alone is insufficient because the current feature
representation does not capture the changed attack mechanism.

## Trust-Aware Diagnostic Layer

A lightweight trust layer was implemented offline over the extracted routing
windows. It computes forwarding trust, rank trust, control-message trust,
route/topology trust and component alert flags. This is a diagnostic feature
layer, not an online RPL defence. It is used to interpret which attack surfaces
are visible to trust-style evidence and whether trust-derived features improve
IDS robustness under drift.

## LLM Explanation Evaluation

The LLM explanation package selects one informative post-activation case from
each attack family. The model-facing evidence includes static IDS context,
adaptation context, feature deltas and trust alerts. Hidden attack labels and
simulator attack markers are excluded from prompts.

Explanations are scored for schema validity, evidence fidelity, mechanism
alignment, uncertainty calibration, drift awareness, actionability and
unsupported claims. This evaluates the LLM as a grounded explanation layer, not
as an intrusion detector.

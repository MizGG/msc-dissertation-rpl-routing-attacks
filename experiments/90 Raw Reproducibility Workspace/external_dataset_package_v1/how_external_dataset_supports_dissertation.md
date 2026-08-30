# How The External Dataset Supports The Dissertation

The external Gope/professor dataset should be used as a supporting baseline,
not as a replacement for the Cooja experiments.

## Correct Interpretation

The external dataset shows that the IDS pipeline can reproduce strong static
classification performance on supplied 6LoWPAN/RPL attack data. This gives
baseline credibility: the models and feature-handling code are capable of
learning known attack patterns when train and test data come from the same
dataset family.

The Cooja experiments provide the main dissertation contribution. They create a
controlled setting where attack families can be changed deliberately, whole
simulation seeds can be kept separate, adaptation data can be varied and a new
Sybil attack surface can be introduced.

In short:

- external dataset: baseline credibility and connection to prior work;
- Cooja dataset: controlled concept-drift, adaptation and new attack-surface
  evidence.

## What Not To Claim

Do not claim that the external dataset proves the Sybil attack works. Sybil is
validated in Cooja.

Do not claim that the external dataset proves the full concept-drift result.
The primary drift result comes from the Cooja cross-attack matrix and
whole-seed adaptation curves.

Do not claim that the baseline reproduction recreates the full adversarial
reinforcement-learning system from the paper. The reproduced component is a
static supervised baseline over the supplied attack CSVs.

## Dissertation Wording

A defensible wording is:

> The supplied external dataset was used to validate the static IDS pipeline
> against existing 6LoWPAN/RPL attack data. The controlled Cooja experiments
> were then used to evaluate attack-distribution drift, whole-seed adaptation
> and the new Sybil identity-manipulation attack surface.

This phrasing keeps the evidence honest and avoids overclaiming.


# RPL Intrusion Detection Under Changed Attack Behaviour

This repository contains the evidence and source code for a controlled RPL intrusion-detection study using Contiki-NG and Cooja.

## Where to start

Open [Evidence/00 Overview](Evidence/00%20Overview). It explains the evidence package and lists the files used to check its integrity.

The main folders are:

- `Evidence/01 Results and Figures`: final tables and publication figures.
- `Evidence/02 Cooja Attack Runs`: Cooja configurations, firmware source, and five attack plus five control runs for each of nine attack families.
- `Evidence/03 IDS Drift and Adaptation`: static cross-attack evaluation, CUSUM/DDM monitoring, and seed-separated adaptation results.
- `Evidence/04 Sybil and Adaptation`: Sybil implementation and evaluation results.
- `Evidence/05 Trust and Defence`: trust evidence, defence evaluation, operational overhead, and robustness checks.
- `Evidence/06 Online External Dataset Validation`: result-only validation packages for external RPL datasets. Raw datasets are not redistributed.
- `Evidence/07 Source Code and Contiki Changes`: analysis scripts and the Contiki-NG patch.
- `Evidence/08 Local LLM Evidence`: local model prompts, outputs for nine cases, and screening results.

## Reproduction

The Cooja configurations are grouped by attack in `Evidence/02 Cooja Attack Runs`. Each scenario uses fixed seeds and a 540-second simulation. Start with [the Cooja reproduction guide](Evidence/02%20Cooja%20Attack%20Runs/COOJA_REPRODUCTION.md), which records the required Contiki-NG revision and patch. Analysis scripts and Contiki-NG modifications are in `Evidence/07 Source Code and Contiki Changes`.

External datasets, presentation files, recordings, dissertation drafts, generated binaries, and earlier exploratory work are deliberately excluded from the tracked submission. The repository contains only the material needed to review the implementation and reported results.

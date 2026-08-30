# Dissertation Evidence Manifest

This is the technical evidence package. The dissertation, Overleaf project and presentation are submitted separately.

| Folder | Contents |
|---|---|
| `01 Final Figures and Tables` | Final figures, source tables and result summaries. |
| `02 Validated Cooja Attacks` | Attack/control code, Cooja configurations and validation summaries. |
| `03 IDS Drift and Adaptation` | Dataset, feature data, cross-attack drift and whole-seed adaptation results. |
| `04 Sybil and Adaptive IDS` | Sybil implementation, rate tests, identity monitoring and adaptive IDS results. |
| `05 Robustness Trust and Defence` | Loss, relocation, trust, sinkhole-defence, overhead and online-monitoring work. |
| `06 External Dataset Comparison` | Supplied Gope data, audit and static-baseline reproduction. |
| `07 Reproducibility Code and Contiki Patch` | Selected analysis scripts and Contiki-NG change records. |
| `08 Local LLM Explanation Evidence` | Structured evidence, local Qwen outputs and screening results. |

## Suggested order

Read `01` for the headline results, `02` and `04` for the Cooja work, then `03`, `05` and `06` for the analysis. `07` and `08` show how the work can be reproduced.

## Notes

All network results come from Cooja simulation, not a physical testbed. The LLM reads structured IDS evidence; it does not detect attacks itself.

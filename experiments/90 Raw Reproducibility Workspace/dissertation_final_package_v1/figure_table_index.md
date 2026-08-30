# Figure and Table Index

## Figures

### Figure 1: Validated Cooja Attack Coverage

File:
`experiments/dissertation_results_summary_v1/figures/attack_coverage.svg`

Use in: Methodology or Results.

Claim supported: the experiment covers nine validated RPL attack families with
matched attack/control evidence.

### Figure 2: Static IDS Failure Under Cross-Attack Drift

File:
`experiments/dissertation_results_summary_v1/figures/static_drift_zero_recall.svg`

Use in: Results.

Claim supported: static IDS models often miss all attack windows when trained
on one attack family and tested on another.

### Figure 3: Whole-Seed Adaptation Curve

File:
`experiments/dissertation_results_summary_v1/figures/overall_adaptation_curve.svg`

Use in: Results and Discussion.

Claim supported: limited target-family adaptation substantially recovers IDS
performance after attack-distribution drift.

### Figure 4: Sybil Static Versus Adapted Performance

File:
`experiments/dissertation_results_summary_v1/figures/sybil_static_vs_adapted.svg`

Use in: Results and Discussion.

Claim supported: Sybil introduces a new identity-manipulation attack surface
that static models handle poorly, while whole-seed adaptation recovers high
held-out performance.

## Tables

### Table 1: Attack Coverage

File:
`experiments/dissertation_results_summary_v1/attack_coverage_table.csv`

Use in: Methodology.

Purpose: summarise attack families, run counts and evidence locations.

### Table 2: Static Concept-Drift Metrics

File:
`experiments/dissertation_results_summary_v1/concept_drift_key_metrics.csv`

Use in: Results.

Purpose: report cross-attack pair counts, zero-recall failures, mean recall and
mean F1.

### Table 3: Adaptation Metrics

File:
`experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv`

Use in: Results.

Purpose: report performance as zero, one, two and three whole target seeds are
added.

### Table 4: External Dataset Baseline

File:
`experiments/external_dataset_package_v1/gope_baseline_results.csv`

Use in: Results or Appendix.

Purpose: show baseline credibility on the supplied Gope/professor dataset.

### Table 5: Cooja Versus External Dataset Scope

File:
`experiments/external_dataset_package_v1/cooja_vs_external_scope_table.csv`

Use in: Methodology.

Purpose: explain why the external dataset and Cooja drift campaign are
complementary rather than merged into one dataset.

### Table 6: Trust-Layer Comparison

File:
`experiments/trust_layer_v1/results/trust_vs_baseline_comparison.csv`

Use in: Discussion or Appendix.

Purpose: report that trust features improve interpretation but did not improve
the CART drift/adaptation metrics.

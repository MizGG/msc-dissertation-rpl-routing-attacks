# Final Figures and Tables

This file lists the final dissertation-facing figures and tables generated from
the validated experiment outputs.

## Figures To Use

1. `figures/attack_coverage.svg`
   - Use in Methodology or Results.
   - Shows the validated Cooja attack campaign.

2. `figures/static_drift_zero_recall.svg`
   - Use in Results.
   - Shows static IDS brittleness under cross-attack drift.

3. `figures/overall_adaptation_curve.svg`
   - Use in Results.
   - Shows recovery as whole target-family adaptation seeds are added.

4. `figures/sybil_static_vs_adapted.svg`
   - Use in Results or Discussion.
   - Shows the new Sybil attack-surface contribution.

## Tables To Use

1. `attack_coverage_table.csv`
   - Use in Methodology.
   - Demonstrates 90 validated Cooja runs across nine attack families.

2. `concept_drift_key_metrics.csv`
   - Use in Results.
   - Reports zero-recall failures and mean cross-attack performance.

3. `adaptation_key_metrics.csv`
   - Use in Results.
   - Reports zero, one, two and three target-seed adaptation performance.

4. `../external_dataset_package_v1/gope_baseline_results.csv`
   - Use in Results or Appendix.
   - Shows external dataset baseline credibility.

5. `../trust_layer_v1/results/trust_vs_baseline_comparison.csv`
   - Use in Discussion or Appendix.
   - Shows trust as an interpretability layer rather than an improved detector.

## Core Narrative

Use the figures in this order:

1. Attack coverage establishes that the Cooja campaign is complete.
2. Static drift failures show that known-attack IDS performance does not
   transfer reliably to changed attack mechanisms.
3. The adaptation curve shows recovery when whole target-family evidence is
   introduced.
4. The Sybil figure shows the original identity-manipulation attack-surface
   contribution.

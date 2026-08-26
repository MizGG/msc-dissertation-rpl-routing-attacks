# Figure and Table Manifest

## Core Tables

- Attack coverage:
  `experiments/dissertation_results_summary_v1/attack_coverage_table.csv`
- Concept drift key metrics:
  `experiments/dissertation_results_summary_v1/concept_drift_key_metrics.csv`
- Adaptation key metrics:
  `experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv`
- Trust comparison:
  `experiments/trust_layer_v1/results/trust_vs_baseline_comparison.csv`
- LLM case index:
  `experiments/llm_explanations_v2/evidence/case_index.csv`
- External dataset baseline:
  `experiments/external_dataset_package_v1/gope_baseline_results.csv`
- Cooja versus external dataset scope:
  `experiments/external_dataset_package_v1/cooja_vs_external_scope_table.csv`
- Presentation/demo guide:
  `experiments/presentation_demo_pack_v1/README.md`

## Core Figures

- Validated attack coverage:
  `experiments/dissertation_results_summary_v1/figures/attack_coverage.svg`
- Static drift zero-recall failures:
  `experiments/dissertation_results_summary_v1/figures/static_drift_zero_recall.svg`
- Overall adaptation curve:
  `experiments/dissertation_results_summary_v1/figures/overall_adaptation_curve.svg`
- Sybil static vs adapted performance:
  `experiments/dissertation_results_summary_v1/figures/sybil_static_vs_adapted.svg`

## Suggested Dissertation Mapping

- Methodology: Cooja setup, attack table, feature extraction, whole-seed split.
- Implementation: attack hooks/apps, Sybil hook, trust layer, LLM package.
- Results: attack validation, static drift, adaptation curve, Sybil result.
- Discussion: feature transfer, concept drift, trust limitations, LLM grounding.
- Limitations: simulation size, Cooja-only evaluation, offline trust, LLM risks.
- Conclusion: static failure, adaptation recovery, Sybil extension and
  explanation layer.

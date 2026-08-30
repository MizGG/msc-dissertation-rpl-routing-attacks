# Figure and Table Manifest

## Core Tables

- Attack coverage:
  `experiments/dissertation_results_summary_v1/attack_coverage_table.csv`
  Use to prove the Cooja campaign scope: nine families, five attack seeds and
  five matched control seeds per family.
- Concept drift key metrics:
  `experiments/dissertation_results_summary_v1/concept_drift_key_metrics.csv`
  Use for the static transfer result: CART has 48 zero-recall failures from 72
  cross-attack pairs; Gaussian is weaker.
- Adaptation key metrics:
  `experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv`
  Use for the recovery result: whole-seed target adaptation raises mean CART F1
  from 0.1822 to 0.8258 after one target seed.
- Trust comparison:
  `experiments/trust_layer_v1/results/trust_vs_baseline_comparison.csv`
  Use as a negative/interpretability result, not as a complete defence result.
- LLM case index:
  `experiments/llm_explanations_v2/evidence/case_index.csv`
  Use only for the explanation-layer methodology unless a live LLM evaluation
  is completed and saved.
- External dataset baseline:
  `experiments/external_dataset_package_v1/gope_baseline_results.csv`
  Use to show baseline credibility on the supplied Gope/professor dataset.
- Cooja versus external dataset scope:
  `experiments/external_dataset_package_v1/cooja_vs_external_scope_table.csv`
  Use to explain why the external data is not merged directly with the Cooja
  drift experiment.
- Presentation/demo guide:
  `experiments/presentation_demo_pack_v1/README.md`

## Core Figures

- Validated attack coverage:
  `experiments/dissertation_results_summary_v1/figures/attack_coverage.svg`
  Results chapter figure for the experimental campaign.
- Static drift zero-recall failures:
  `experiments/dissertation_results_summary_v1/figures/static_drift_zero_recall.svg`
  Results chapter figure for static IDS brittleness under cross-attack drift.
- Overall adaptation curve:
  `experiments/dissertation_results_summary_v1/figures/overall_adaptation_curve.svg`
  Results chapter figure for recovery as target-family adaptation data is added.
- Sybil static vs adapted performance:
  `experiments/dissertation_results_summary_v1/figures/sybil_static_vs_adapted.svg`
  Results/discussion figure for the new attack-surface contribution.

## Core Argument Source

- Dissertation core argument:
  `experiments/dissertation_results_summary_v1/core_argument.md`
  Use this as the stable source for the abstract, introduction contribution
  paragraph, discussion opening and viva/presentation answer.

## Suggested Dissertation Mapping

- Methodology: Cooja setup, attack table, feature extraction, whole-seed split.
- Implementation: attack hooks/apps, Sybil hook, trust layer, LLM package.
- Results: attack validation, static drift, adaptation curve, Sybil result.
- Discussion: feature transfer, concept drift, trust limitations, LLM grounding.
- Limitations: simulation size, Cooja-only evaluation, offline trust, LLM risks.
- Conclusion: static failure, adaptation recovery, Sybil extension and
  explanation layer.

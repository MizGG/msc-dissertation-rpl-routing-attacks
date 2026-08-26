# Terminal Commands

Run these from the repository root:

```sh
cd /Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood
```

## Quick Status

```sh
git log --oneline -10
```

## Show Attack Validation

```sh
column -s, -t experiments/dissertation_results_summary_v1/attack_coverage_table.csv
```

## Show Sybil Validation

```sh
column -s, -t experiments/sybil_attack_v1/validation_summary.csv
```

Expected point:

- 5 attack runs have 150-151 spoofed DIO identity events.
- 5 control runs have 0 Sybil events.

## Show Concept Drift Metrics

```sh
column -s, -t experiments/dissertation_results_summary_v1/concept_drift_key_metrics.csv
```

Expected point:

- CART has 48 zero-recall failures out of 72 cross-attack pairs.
- Sybil-related CART pairs have 11 zero-recall failures out of 16.

## Show Adaptation Metrics

```sh
column -s, -t experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv
```

Expected point:

- Overall F1 improves from 0.1822 with no target seeds to 0.8258 with one
  target seed.
- Sybil target F1 improves from 0.2183 to 0.9683 with one Sybil seed.

## Show Core Argument

```sh
sed -n '1,120p' experiments/dissertation_results_summary_v1/core_argument.md
```

Expected point:

- Static IDS models fail under cross-attack drift.
- Whole-seed adaptation recovers performance.
- Sybil is the new attack-surface contribution.
- Feature representation determines whether adaptation can work.

## Optional: Regenerate LLM Evidence Later

```sh
python3 scripts/build_llm_explanation_package_v2.py
python3 scripts/generate_llm_explanation_fixture_v2.py
```

Important: this is only a deterministic pipeline check unless a live model run
is completed and raw model outputs are preserved.

```sh
python3 scripts/score_llm_explanations_v2.py \
  --outputs experiments/llm_explanations_v2/outputs/deterministic_explanations.jsonl \
  --out-dir experiments/llm_explanations_v2/evaluation/scored_deterministic
```

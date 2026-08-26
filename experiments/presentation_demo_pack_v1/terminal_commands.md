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

## Regenerate LLM Evidence

```sh
python3 scripts/build_llm_explanation_package_v2.py
```

Expected output:

```text
Wrote 9 LLM explanation cases to experiments/llm_explanations_v2
```

## Generate Demo Explanations

```sh
python3 scripts/generate_llm_explanation_fixture_v2.py
```

Expected output:

```text
Wrote 9 deterministic explanation outputs to experiments/llm_explanations_v2/outputs/deterministic_explanations.jsonl
```

## Score Demo Explanations

```sh
python3 scripts/score_llm_explanations_v2.py \
  --outputs experiments/llm_explanations_v2/outputs/deterministic_explanations.jsonl \
  --out-dir experiments/llm_explanations_v2/evaluation/scored_deterministic
```

Expected output:

```text
{"cases": 9, "mean_score_out_of_10": 10.0, "schema_validity_rate": 1.0, "unsupported_claim_rate": 0.0}
```

Important: explain that this is a deterministic demo/scorer fixture, not live
external LLM performance.


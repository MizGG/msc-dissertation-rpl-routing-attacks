#!/bin/sh
set -eu

cd /Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood

echo "== Recent commits =="
git log --oneline -5

echo
echo "== Attack coverage =="
column -s, -t experiments/dissertation_results_summary_v1/attack_coverage_table.csv

echo
echo "== Sybil validation =="
column -s, -t experiments/sybil_attack_v1/validation_summary.csv

echo
echo "== Concept drift key metrics =="
column -s, -t experiments/dissertation_results_summary_v1/concept_drift_key_metrics.csv

echo
echo "== Adaptation key metrics =="
column -s, -t experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv

echo
echo "== LLM explanation package =="
python3 scripts/build_llm_explanation_package_v2.py
python3 scripts/generate_llm_explanation_fixture_v2.py
python3 scripts/score_llm_explanations_v2.py \
  --outputs experiments/llm_explanations_v2/outputs/deterministic_explanations.jsonl \
  --out-dir experiments/llm_explanations_v2/evaluation/scored_deterministic

echo
echo "== Demo check complete =="

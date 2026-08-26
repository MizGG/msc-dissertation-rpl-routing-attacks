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
echo "== Core argument =="
sed -n '1,80p' experiments/dissertation_results_summary_v1/core_argument.md

echo
echo "== Demo check complete =="

# Live Demo Plan

Do not rely on running full Cooja simulations live during the presentation.
They are slow and brittle under time pressure. Use preserved validated evidence
and, if needed, show a short recorded Cooja clip separately.

## Safe Demo Flow

1. Open the validated results folder:

   `experiments/dissertation_results_summary_v1`

2. Show attack coverage:

   `experiments/dissertation_results_summary_v1/attack_coverage_table.csv`

3. Show one Cooja evidence folder:

   `experiments/sybil_attack_v1/runs/SYBIL_ATTACK_N16_SEED123456`

   Point to `COOJA.testlog` lines containing:

   - `SYBIL ATTACK: enabled`
   - `SYBIL: sending RPL DIO as virtual identity`

4. Show concept drift result:

   `experiments/cross_attack_drift_with_sybil_v1/results/cross_attack_matrix.csv`

5. Show adaptation result:

   `experiments/cross_attack_adaptation_with_sybil_v1/cross_attack_adaptation_summary.csv`

6. Regenerate LLM explanation cases:

   ```sh
   python3 scripts/build_llm_explanation_package_v2.py
   ```

7. Show the model-facing prompt file:

   `experiments/llm_explanations_v2/prompts/explanation_requests.jsonl`

8. Validate the scoring pipeline without an API call:

   ```sh
   python3 scripts/score_llm_explanations_v2.py \
     --outputs experiments/llm_explanations_v2/evaluation/handcrafted_schema_fixture.jsonl
   ```

9. Show the deterministic explanation demo:

   ```sh
   python3 scripts/generate_llm_explanation_fixture_v2.py
   python3 scripts/score_llm_explanations_v2.py \
     --outputs experiments/llm_explanations_v2/outputs/deterministic_explanations.jsonl \
     --out-dir experiments/llm_explanations_v2/evaluation/scored_deterministic
   ```

   Explain clearly that this validates the evidence-to-explanation-to-scoring
   pipeline. It is not being claimed as external LLM performance.

## Recorded Cooja Clips

Record short clips in advance if possible:

- blackhole activation and packet-drop log marker;
- sinkhole advertised-rank marker;
- Sybil virtual-identity DIO marker;
- one control run showing no attack marker.

The recording is backup evidence. The live demo should focus on reproducible
files and scripts, because those are less likely to fail.

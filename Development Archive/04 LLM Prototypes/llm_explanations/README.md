# Evidence-Grounded LLM Explanation Layer

This package converts the verified routing IDS and CUSUM outputs into five
held-out alert-explanation cases. It deliberately separates three layers:

- `evidence/alerts.jsonl`: label-free evidence presented to an explainer;
- `prompts/explanation_requests.jsonl`: constrained system and user messages;
- `evaluation/evaluation_cases.jsonl`: hidden ground truth, required facts,
  forbidden claims and an eight-point scoring rubric.
- `evaluation/handcrafted_schema_fixture.jsonl`: a non-LLM fixture used only to
  test the response schema and scorer.

Run from the repository root:

```text
python3 scripts/build_llm_explanation_package.py
```

The explainer receives generic routing state, the CUSUM score/threshold and
static-versus-adapted IDS context. It does not receive attack activation logs,
attack labels, node identities or the hidden evaluation rubric.

No live LLM response is currently stored. The secure API-key setup did not
complete, so these files are the reproducible offline boundary for a later live
model evaluation. Do not manually place an API key in this directory or commit
one to Git.

## Evaluation Protocol

For each request, store the raw model JSON separately and score it blind against
the corresponding evaluation case. Score evidence fidelity, mechanism
alignment, uncertainty calibration and actionability from 0 to 2. Report the
mean total, unsupported-claim rate and JSON-validity rate. Five cases are enough
for a dissertation demonstration, but not for broad claims about explanation
quality.

Validate the scorer without making an API request:

```text
python3 scripts/score_llm_explanations.py \
  --outputs experiments/llm_explanations/evaluation/handcrafted_schema_fixture.jsonl
```

The fixture score is a software check and must never be reported as model
performance.

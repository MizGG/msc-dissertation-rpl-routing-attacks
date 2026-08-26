# LLM Explanation Layer V2

This package builds a multi-attack, evidence-grounded LLM explanation layer for
the dissertation.

The LLM is not the IDS. The IDS, cross-attack drift experiment, adaptation
experiment and trust diagnostics produce structured evidence. The LLM receives
that evidence and explains what changed, why a static model may struggle under
concept drift, what remains uncertain and what an analyst should check next.

## Contents

- `evidence/attack_explanation_cases.jsonl`: one structured evidence case for
  each of the nine attack families.
- `prompts/explanation_requests.jsonl`: model-facing prompt messages.
- `evaluation/evaluation_cases.jsonl`: hidden rubrics used for scoring.
- `evaluation/handcrafted_schema_fixture.jsonl`: non-LLM fixture for testing
  the scorer and response schema.
- `evaluation/scored/`: scorer output for the handcrafted fixture.
- `outputs/deterministic_explanations.jsonl`: deterministic local
  model-style explanations generated from the evidence for demo/testing.
- `evaluation/scored_deterministic/`: scorer output for deterministic
  explanations.

## Current Scope

The package covers:

- blackhole;
- sinkhole;
- DIS flood;
- grayhole;
- increase-rank;
- DIO suppression;
- worst-parent;
- wormhole;
- Sybil.

The model-facing evidence excludes hidden ground-truth labels and simulator
attack markers. It includes IDS context, adaptation context, routing-window
feature differences and trust alerts.

## Reproduce

From the repository root:

```sh
python3 scripts/build_llm_explanation_package_v2.py
python3 scripts/score_llm_explanations_v2.py \
  --outputs experiments/llm_explanations_v2/evaluation/handcrafted_schema_fixture.jsonl
python3 scripts/generate_llm_explanation_fixture_v2.py
python3 scripts/score_llm_explanations_v2.py \
  --outputs experiments/llm_explanations_v2/outputs/deterministic_explanations.jsonl \
  --out-dir experiments/llm_explanations_v2/evaluation/scored_deterministic
```

The handcrafted fixture and deterministic explanation score are software/demo
checks only. They must not be reported as external live LLM performance.

## Dissertation Claim

The defensible claim is:

> The LLM explanation layer converts structured IDS, drift, adaptation and trust
> evidence into analyst-readable explanations. It is evaluated for faithfulness,
> mechanism alignment, uncertainty calibration, drift awareness, actionability
> and unsupported-claim rate.

Do not claim that the LLM detects attacks directly.

For a final live LLM experiment, run the prompt file against one fixed model,
preserve the raw outputs, and score those raw outputs with
`score_llm_explanations_v2.py`.

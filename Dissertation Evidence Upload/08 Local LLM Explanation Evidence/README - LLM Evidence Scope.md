# Local LLM Evidence

This folder records the local Qwen explanation workflow. The LLM receives structured IDS, drift, adaptation and trust evidence. It is not the IDS or the drift detector.

- `Actual Local Model Output/ollama_full_9_cases.jsonl` is the nine-case batch produced locally with Ollama and `qwen2.5:3b`.
- `Automatic Screening/ollama_full_9_cases_scores.csv` and `ollama_full_9_cases_summary.json` contain the screening result: nine valid responses, mean score 7.7778/10 and no unsupported-claim penalties.
- `Evidence and Prompts` contains the evidence cases and the exact prompts.

The Sinkhole and case-01 files are earlier one-case demonstrations.

The screening checks structure, evidence references, uncertainty, drift discussion, next steps and unsupported claims. It is not a factuality benchmark, a human study or an IDS metric.

The local runner and scorer are in `07 Reproducibility Code and Contiki Patch/Analysis Source Code/04 Local LLM Explanation Layer`.

#!/usr/bin/env python3
"""Run evidence-grounded explanation prompts against a local Ollama model.

No API key or cloud service is used. The input and output JSONL schemas are
compatible with score_llm_explanations_v2.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

REQUIRED_KEYS = {
    "summary",
    "observed_change",
    "likely_mechanism",
    "drift_implication",
    "confidence",
    "limitations",
    "recommended_action",
}
DEFAULT_PROMPTS = Path(
    "experiments/90 Raw Reproducibility Workspace/llm_explanations_v2/"
    "prompts/explanation_requests.jsonl"
)
DEFAULT_OUTPUT = Path(
    "experiments/90 Raw Reproducibility Workspace/llm_explanations_v2/"
    "outputs/ollama_explanations.jsonl"
)


def read_jsonl(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def request_response(endpoint: str, model: str, messages: list[object]) -> dict[str, object]:
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }
    ).encode("utf-8")
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=180) as response:
        body = json.loads(response.read().decode("utf-8"))
    content = body.get("message", {}).get("content")
    if not isinstance(content, str):
        raise ValueError("Ollama response does not contain message.content")
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise ValueError("Ollama response content is not a JSON object")
    missing = sorted(REQUIRED_KEYS - set(parsed))
    if missing:
        raise ValueError(f"Ollama response is missing required keys: {', '.join(missing)}")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5:3b")
    parser.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434/api/chat")
    parser.add_argument("--limit", type=int, default=None, help="Run only the first N prompt cases")
    args = parser.parse_args()

    prompts = read_jsonl(args.prompts)
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit must be at least 1")
        prompts = prompts[:args.limit]
    outputs: list[dict[str, object]] = []
    try:
        for index, prompt in enumerate(prompts, start=1):
            alert_id = prompt.get("alert_id")
            messages = prompt.get("messages")
            if not isinstance(alert_id, str) or not isinstance(messages, list):
                raise ValueError(f"Prompt {index} has an invalid alert_id or messages field")
            outputs.append(
                {
                    "alert_id": alert_id,
                    "response": request_response(args.ollama_url, args.model, messages),
                }
            )
            print(f"Completed {index}/{len(prompts)}: {alert_id}", file=sys.stderr)
    except URLError as error:
        raise SystemExit(
            "Cannot reach Ollama. Start it with `ollama serve` and make sure the requested "
            f"model is installed: `ollama pull {args.model}`. Details: {error.reason}"
        ) from error

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for row in outputs:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"Wrote {len(outputs)} local Ollama explanations to {args.out}")


if __name__ == "__main__":
    main()

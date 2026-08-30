#!/usr/bin/env python3
"""Score structured alert explanations against the hidden evidence rubric."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ACTION_WORDS = ("inspect", "verify", "monitor", "isolate", "review", "capture")
UNCERTAINTY_WORDS = ("likely", "possible", "may", "might", "suggest", "consistent with")
CERTAINTY_WORDS = ("definitively", "is a proven attack", "proves this attack", "certainly compromised")
UNSUPPORTED_PHRASES = ("node 16", "packet dropping was observed", "entire topology changed")


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on {path}:{line_number}: {error}") from error
    return rows


def flattened(response: dict[str, object]) -> str:
    return " ".join(str(value) for value in response.values()).lower()


def score_case(output: dict[str, object], rubric: dict[str, object]) -> dict[str, object]:
    response = output.get("response")
    if not isinstance(response, dict):
        raise ValueError(f"{output.get('alert_id')}: response must be a JSON object")
    text = flattened(response)

    rank_fact = all(token in text for token in ("128", "256", "rank"))
    pair_fact = "5" in text and "pair" in text
    cusum_fact = all(token in text for token in ("cusum", "11", "0.5"))
    fact_count = sum((rank_fact, pair_fact, cusum_fact))
    evidence_fidelity = 2 if fact_count == 3 else 1 if fact_count else 0

    mechanism_terms = "rank" in text and any(
        term in text for term in ("sinkhole", "parent attraction", "routing manipulation")
    )
    mechanism_alignment = 2 if mechanism_terms else 1 if "rank" in text else 0

    uncertain = any(term in text for term in UNCERTAINTY_WORDS)
    overcertain = any(term in text for term in CERTAINTY_WORDS)
    uncertainty_calibration = 2 if uncertain and not overcertain else 1 if not overcertain else 0

    action = str(response.get("recommended_action", "")).lower()
    actionability = 2 if action and any(word in action for word in ACTION_WORDS) else 1 if action else 0

    unsupported = sorted({phrase for phrase in UNSUPPORTED_PHRASES if phrase in text})
    total = evidence_fidelity + mechanism_alignment + uncertainty_calibration + actionability
    required_facts = rubric.get("required_facts", [])
    return {
        "alert_id": output["alert_id"],
        "evidence_fidelity": evidence_fidelity,
        "mechanism_alignment": mechanism_alignment,
        "uncertainty_calibration": uncertainty_calibration,
        "actionability": actionability,
        "total": total,
        "unsupported_claim": int(bool(unsupported)),
        "unsupported_phrases": "; ".join(unsupported),
        "required_fact_count": len(required_facts) if isinstance(required_facts, list) else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument(
        "--rubric",
        type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/llm_explanations/evaluation/evaluation_cases.jsonl"),
    )
    parser.add_argument(
        "--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/llm_explanations/evaluation/scored")
    )
    args = parser.parse_args()

    outputs = read_jsonl(args.outputs)
    rubrics = {str(row["alert_id"]): row for row in read_jsonl(args.rubric)}
    if {str(row.get("alert_id")) for row in outputs} != set(rubrics):
        raise ValueError("Output alert IDs do not exactly match the evaluation cases")
    scores = [score_case(row, rubrics[str(row["alert_id"])]) for row in outputs]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "case_scores.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scores[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(scores)
    summary = {
        "cases": len(scores),
        "mean_total_score_out_of_8": round(sum(int(row["total"]) for row in scores) / len(scores), 4),
        "unsupported_claim_rate": round(
            sum(int(row["unsupported_claim"]) for row in scores) / len(scores), 4
        ),
        "json_validity_rate": 1.0,
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

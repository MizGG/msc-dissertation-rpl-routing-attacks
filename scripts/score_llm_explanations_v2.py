#!/usr/bin/env python3
"""Score multi-attack LLM explanations against hidden rubrics."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


UNCERTAINTY = ("likely", "possible", "may", "might", "suggest", "consistent with", "inferred")
DRIFT = ("drift", "distribution", "generalisation", "generalization", "static", "adaptation")
ACTION = ("inspect", "verify", "monitor", "review", "investigate", "compare", "capture")
FORBIDDEN = (
    "proven the exact compromised physical node",
    "cryptographic identity compromise was observed",
    "attack was prevented by the trust layer",
    "all future attacks",
)


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on {path}:{line_number}: {error}") from error
    return rows


def flatten(value: object) -> str:
    if isinstance(value, dict):
        return " ".join(flatten(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return str(value)


def score(output: dict[str, object], rubric: dict[str, object]) -> dict[str, object]:
    response = output.get("response")
    if not isinstance(response, dict):
        raise ValueError(f"{output.get('alert_id')}: response must be an object")
    required_keys = {
        "summary",
        "observed_change",
        "likely_mechanism",
        "drift_implication",
        "confidence",
        "limitations",
        "recommended_action",
    }
    missing = sorted(required_keys - set(response))
    text = flatten(response).lower()
    expected_terms = [str(term).lower() for term in rubric.get("expected_terms", [])]
    mechanism_hits = sum(1 for term in expected_terms if term in text)
    feature_words = (
        "trust",
        "rank",
        "dio",
        "dis",
        "forwarding",
        "route",
        "parent",
        "identity",
        "topology",
        "control",
    )
    evidence_fidelity = 2 if any(word in text for word in feature_words) else 0
    mechanism_alignment = 2 if mechanism_hits >= min(2, len(expected_terms)) else 1 if mechanism_hits else 0
    uncertainty = 2 if any(word in text for word in UNCERTAINTY) else 0
    drift_alignment = 2 if any(word in text for word in DRIFT) else 0
    actionability = 2 if any(word in str(response.get("recommended_action", "")).lower() for word in ACTION) else 0
    schema = 2 if not missing and str(response.get("confidence", "")).lower() in {"low", "medium", "high"} else 0
    unsupported = sorted(phrase for phrase in FORBIDDEN if phrase in text)
    raw_total = evidence_fidelity + mechanism_alignment + uncertainty + drift_alignment + actionability + schema
    penalty = 2 if unsupported else 0
    return {
        "alert_id": output["alert_id"],
        "ground_truth_family": rubric["ground_truth_for_evaluation_only"],
        "schema": schema,
        "evidence_fidelity": evidence_fidelity,
        "mechanism_alignment": mechanism_alignment,
        "uncertainty_calibration": uncertainty,
        "drift_alignment": drift_alignment,
        "actionability": actionability,
        "unsupported_claim_penalty": penalty,
        "total_out_of_10": max(0, min(10, raw_total - penalty)),
        "missing_keys": ";".join(missing),
        "unsupported_claims": ";".join(unsupported),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument(
        "--rubric",
        type=Path,
        default=Path("experiments/llm_explanations_v2/evaluation/evaluation_cases.jsonl"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/llm_explanations_v2/evaluation/scored"),
    )
    args = parser.parse_args()

    outputs = read_jsonl(args.outputs)
    rubrics = {str(row["alert_id"]): row for row in read_jsonl(args.rubric)}
    if {str(row.get("alert_id")) for row in outputs} != set(rubrics):
        raise ValueError("Output alert IDs do not exactly match evaluation cases")
    scores = [score(row, rubrics[str(row["alert_id"])]) for row in outputs]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "case_scores.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scores[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(scores)
    summary = {
        "cases": len(scores),
        "mean_score_out_of_10": round(sum(float(row["total_out_of_10"]) for row in scores) / len(scores), 4),
        "unsupported_claim_rate": round(sum(1 for row in scores if row["unsupported_claims"]) / len(scores), 4),
        "schema_validity_rate": round(sum(1 for row in scores if not row["missing_keys"]) / len(scores), 4),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate deterministic evidence-grounded explanation outputs for LLM v2 cases.

This is a local fixture generator. It produces model-style explanations from the
same evidence format that a live LLM would receive. Use it for dissertation
pipeline demonstration and scorer validation, not as external-model performance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path



def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")



def format_changes(changes: list[object]) -> str:
    parts: list[str] = []
    for item in changes[:4]:
        if not isinstance(item, dict):
            continue
        parts.append(
            f"{item['feature']} changed from {item['matched_control']} "
            f"to {item['observed']} (delta {item['delta']})"
        )
    return "; ".join(parts)


def explanation(case: dict[str, object]) -> dict[str, object]:
    context = case["model_context"]
    assert isinstance(context, dict)
    static = context["static_cross_attack_context"]
    adaptation = context["adaptation_context"]
    assert isinstance(static, dict)
    assert isinstance(adaptation, dict)
    changes = case["top_feature_changes"]
    assert isinstance(changes, list)
    trust_alerts = case["trust_alerts"]
    assert isinstance(trust_alerts, dict)
    active_trust = [name for name, value in trust_alerts.items() if int(value) == 1]
    trust_text = ", ".join(active_trust) if active_trust else "no trust alert fired in this selected window"

    static_recall = static["static_recall"]
    static_f1 = static["static_f1"]
    adapted_f1 = adaptation["mean_f1_with_1_target_seed"]
    return {
        "summary": (
            "The selected RPL window shows evidence that should be treated as "
            "possible attack-distribution drift rather than a standalone attack proof."
        ),
        "observed_change": (
            f"The strongest supplied differences are: {format_changes(changes)}. "
            f"The trust evidence reports {trust_text}."
        ),
        "likely_mechanism": (
            "The supplied evidence indicates a likely RPL forwarding, routing, or control-plane anomaly. "
            "It does not by itself identify a specific attack family."
        ),
        "drift_implication": (
            f"The static cross-attack context reports recall {static_recall} and F1 {static_f1}, "
            f"while one target adaptation seed gives mean F1 {adapted_f1}. This suggests the "
            "static IDS may not generalise to the changed mechanism, whereas adaptation can recover."
        ),
        "confidence": "medium",
        "limitations": (
            "The evidence does not prove the exact compromised physical node, cryptographic identity "
            "compromise, or that the trust layer prevented the attack."
        ),
        "recommended_action": (
            "Inspect the affected routing-window features and trust alerts, compare them with matched "
            "control windows, and review whether additional target-family data is needed before acting."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/llm_explanations_v2/evidence/attack_explanation_cases.jsonl"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/llm_explanations_v2/outputs/deterministic_explanations.jsonl"),
    )
    args = parser.parse_args()

    outputs = [
        {"alert_id": str(case["alert_id"]), "response": explanation(case)}
        for case in read_jsonl(args.cases)
    ]
    write_jsonl(args.out, outputs)
    print(f"Wrote {len(outputs)} deterministic explanation outputs to {args.out}")


if __name__ == "__main__":
    main()

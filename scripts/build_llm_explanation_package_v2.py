#!/usr/bin/env python3
"""Build multi-attack LLM explanation cases from drift, trust and Cooja evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_FEATURES = Path("experiments/trust_layer_v1/features/trust_routing_window_features.csv")
DEFAULT_DRIFT = Path("experiments/cross_attack_drift_with_sybil_v1/results/cross_attack_matrix.csv")
DEFAULT_ADAPT = Path("experiments/cross_attack_adaptation_with_sybil_v1/cross_attack_adaptation_summary.csv")
DEFAULT_OUT = Path("experiments/llm_explanations_v2")

CASE_FEATURES = [
    "app_rx_delta",
    "app_missed_delta",
    "radio_tx_count",
    "attacker_node16_radio_tx",
    "dio_rx_count",
    "dio_tx_count",
    "dis_tx_count",
    "dao_tx_count",
    "parent_switch_count",
    "unique_dio_senders",
    "dio_rx_low_rank_nonroot_count",
    "state_nonroot_rank_min",
    "state_low_rank_nonroot_pairs",
    "state_receivers_exposed_low_rank_nonroot",
    "topology_mean_depth",
    "topology_max_depth",
    "trust_forwarding",
    "trust_rank",
    "trust_control",
    "trust_route",
    "trust_total",
    "trust_forwarding_alert",
    "trust_rank_alert",
    "trust_control_alert",
    "trust_route_alert",
    "trust_any_alert",
]

EXPECTED_MECHANISMS = {
    "blackhole": "forwarding loss or blackhole-style packet dropping",
    "grayhole": "selective forwarding or grayhole-style intermittent loss",
    "sinkhole": "rank manipulation or sinkhole-like parent attraction",
    "increase_rank": "rank manipulation or abnormal rank advertisement",
    "dis_flood": "RPL DIS control-message flooding",
    "dio_suppression": "RPL DIO suppression or missing control-plane advertisements",
    "worst_parent": "route instability or malicious parent-selection behaviour",
    "wormhole": "topology shortcut or wormhole-like radio adjacency anomaly",
    "sybil": "identity manipulation or Sybil-like DIO source churn",
}

EXPECTED_TERMS = {
    "blackhole": ["forwarding", "loss"],
    "grayhole": ["selective", "forwarding"],
    "sinkhole": ["rank", "sinkhole"],
    "increase_rank": ["rank"],
    "dis_flood": ["dis", "flood"],
    "dio_suppression": ["dio", "suppression"],
    "worst_parent": ["parent", "route"],
    "wormhole": ["wormhole", "topology"],
    "sybil": ["identity", "sybil"],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(text: str) -> int | float:
    value = float(text or 0)
    return int(value) if value.is_integer() else round(value, 4)


def find_one(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    matches = [row for row in rows if all(row.get(key) == value for key, value in criteria.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {criteria}; found {len(matches)}")
    return matches[0]


def select_static_context(drift_rows: list[dict[str, str]], family: str) -> dict[str, object]:
    row = find_one(
        drift_rows,
        evaluation="cross_attack",
        model="cart",
        train_family="blackhole",
        test_family=family,
    ) if family != "blackhole" else find_one(
        drift_rows,
        evaluation="cross_attack",
        model="cart",
        train_family="sinkhole",
        test_family="blackhole",
    )
    return {
        "source_training_family": row["train_family"],
        "target_evaluation_family_hidden_from_prompt": row["test_family"],
        "static_accuracy": number(row["accuracy"]),
        "static_precision": number(row["precision"]),
        "static_recall": number(row["recall"]),
        "static_f1": number(row["f1"]),
        "false_negatives": number(row["fn"]),
        "false_positives": number(row["fp"]),
    }


def select_adaptation_context(adapt_rows: list[dict[str, str]], family: str) -> dict[str, object]:
    subset = [
        row for row in adapt_rows
        if row["target_family"] == family and row["adaptation_seed_count"] in {"0", "1"}
    ]
    output: dict[str, object] = {}
    for count in ("0", "1"):
        rows = [row for row in subset if row["adaptation_seed_count"] == count]
        output[f"mean_f1_with_{count}_target_seed"] = round(
            sum(float(row["mean_f1"]) for row in rows) / len(rows), 4
        )
        output[f"mean_recall_with_{count}_target_seed"] = round(
            sum(float(row["mean_recall"]) for row in rows) / len(rows), 4
        )
    return output


def feature_snapshot(observed: dict[str, str], reference: dict[str, str]) -> dict[str, object]:
    output: dict[str, object] = {}
    for field in CASE_FEATURES:
        obs = number(observed.get(field, "0"))
        ref = number(reference.get(field, "0"))
        output[field] = {
            "observed": obs,
            "matched_control": ref,
            "delta": round(float(obs) - float(ref), 4),
        }
    return output


def top_changes(snapshot: dict[str, object], limit: int = 8) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for field, payload in snapshot.items():
        if not isinstance(payload, dict):
            continue
        observed = float(payload["observed"])
        reference = float(payload["matched_control"])
        delta = float(payload["delta"])
        scale = max(abs(observed), abs(reference), 1.0)
        rows.append({
            "feature": field,
            "observed": payload["observed"],
            "matched_control": payload["matched_control"],
            "delta": payload["delta"],
            "relative_change": round(abs(delta) / scale, 4),
        })
    rows.sort(key=lambda row: (float(row["relative_change"]), abs(float(row["delta"]))), reverse=True)
    return rows[:limit]


def evidence_score(snapshot: dict[str, object]) -> float:
    score = 0.0
    for row in top_changes(snapshot, limit=len(snapshot)):
        score += float(row["relative_change"]) + min(abs(float(row["delta"])) / 100.0, 1.0)
    return score


def select_case_window(
    rows: list[dict[str, str]],
    family: str,
    seed: str,
    requested_window_start: str | None,
) -> tuple[dict[str, str], dict[str, str], dict[str, object]]:
    if requested_window_start is not None:
        observed = find_one(rows, family=family, mode="attack", seed=seed, window_start_s=requested_window_start)
        reference = find_one(rows, family=family, mode="control", seed=seed, window_start_s=requested_window_start)
        return observed, reference, feature_snapshot(observed, reference)

    attack_windows = [
        row for row in rows
        if row["family"] == family and row["mode"] == "attack" and row["seed"] == seed
        and int(row["window_start_s"]) >= 240
    ]
    if not attack_windows:
        raise ValueError(f"No post-activation windows for {family} seed {seed}")
    best: tuple[float, dict[str, str], dict[str, str], dict[str, object]] | None = None
    for observed in attack_windows:
        reference = find_one(
            rows,
            family=family,
            mode="control",
            seed=seed,
            window_start_s=observed["window_start_s"],
        )
        snapshot = feature_snapshot(observed, reference)
        score = evidence_score(snapshot)
        if best is None or score > best[0]:
            best = (score, observed, reference, snapshot)
    assert best is not None
    return best[1], best[2], best[3]


def reference_response(family: str, evidence: dict[str, object]) -> dict[str, object]:
    changes = evidence["top_feature_changes"]
    assert isinstance(changes, list)
    names = [str(row["feature"]) for row in changes[:3] if isinstance(row, dict)]
    return {
        "summary": "The alert window differs from its matched control in routing/trust behaviour.",
        "observed_change": f"The largest observed changes involve {', '.join(names)}.",
        "likely_mechanism": f"This is consistent with likely {EXPECTED_MECHANISMS[family]}.",
        "drift_implication": "A static IDS trained on a different attack surface may miss this behaviour because the changed mechanism shifts the feature distribution.",
        "confidence": "medium",
        "limitations": "The evidence supports an attack mechanism hypothesis, not a cryptographic proof of attacker identity or intent.",
        "recommended_action": "Inspect the affected routing, trust and control-message evidence before changing routing policy.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--drift", type=Path, default=DEFAULT_DRIFT)
    parser.add_argument("--adaptation", type=Path, default=DEFAULT_ADAPT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", default="123456")
    parser.add_argument(
        "--window-start",
        default=None,
        help="Optional fixed 60-second window start. By default, choose the most informative post-activation window per family.",
    )
    args = parser.parse_args()

    features = read_csv(args.features)
    drift = read_csv(args.drift)
    adaptation = read_csv(args.adaptation)
    families = sorted({row["family"] for row in features})

    evidence_rows: list[dict[str, object]] = []
    prompt_rows: list[dict[str, object]] = []
    evaluation_rows: list[dict[str, object]] = []
    fixture_rows: list[dict[str, object]] = []
    index_rows: list[dict[str, object]] = []

    system_prompt = (
        "You explain RPL/6LoWPAN IDS and concept-drift evidence to a security analyst. "
        "Use only the supplied evidence. Do not invent attacker node IDs, packet captures, "
        "or ground-truth labels. Distinguish observation from inference. Return valid JSON "
        "with keys summary, observed_change, likely_mechanism, drift_implication, confidence, "
        "limitations and recommended_action. confidence must be low, medium or high."
    )

    for family in families:
        observed, reference, snapshot = select_case_window(features, family, args.seed, args.window_start)
        window_start = int(observed["window_start_s"])
        alert_id = f"rpl-{family}-{args.seed}-{window_start}"
        evidence = {
            "alert_id": alert_id,
            "network": "Contiki-NG/Cooja RPL-lite 6LoWPAN",
            "window": {
                "start_s": window_start,
                "end_s": window_start + 60,
                "matched_control_seed": args.seed,
            },
            "model_context": {
                "task": "explain why this target window may represent attack-distribution drift",
                "static_cross_attack_context": {
                    key: value for key, value in select_static_context(drift, family).items()
                    if key != "target_evaluation_family_hidden_from_prompt"
                },
                "adaptation_context": select_adaptation_context(adaptation, family),
            },
            "observed_vs_matched_control": snapshot,
            "top_feature_changes": top_changes(snapshot),
            "trust_alerts": {
                field: int(float(observed[field]))
                for field in (
                    "trust_forwarding_alert",
                    "trust_rank_alert",
                    "trust_control_alert",
                    "trust_route_alert",
                    "trust_any_alert",
                )
            },
        }
        evidence_rows.append(evidence)
        prompt_rows.append({
            "alert_id": alert_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(evidence, sort_keys=True)},
            ],
        })
        evaluation_rows.append({
            "alert_id": alert_id,
            "ground_truth_for_evaluation_only": family,
            "expected_mechanism": EXPECTED_MECHANISMS[family],
            "expected_terms": EXPECTED_TERMS[family],
            "required_discussion": [
                "must mention at least one supplied feature/trust change",
                "must describe mechanism as likely/inferred rather than proven",
                "must connect the evidence to concept drift or static model generalisation",
            ],
            "forbidden_unsupported_claims": [
                "the model has proven the exact compromised physical node",
                "cryptographic identity compromise was observed",
                "the attack was prevented by the trust layer",
                "all future attacks of this type will be detected",
            ],
            "maximum_score": 10,
        })
        fixture_rows.append({
            "alert_id": alert_id,
            "response": reference_response(family, evidence),
        })
        index_rows.append({
            "alert_id": alert_id,
            "family_hidden_from_prompt": family,
            "seed": args.seed,
            "window_start_s": window_start,
            "window_end_s": window_start + 60,
            "top_feature_1": evidence["top_feature_changes"][0]["feature"],
            "top_feature_2": evidence["top_feature_changes"][1]["feature"],
            "top_feature_3": evidence["top_feature_changes"][2]["feature"],
            "trust_forwarding_alert": evidence["trust_alerts"]["trust_forwarding_alert"],
            "trust_rank_alert": evidence["trust_alerts"]["trust_rank_alert"],
            "trust_control_alert": evidence["trust_alerts"]["trust_control_alert"],
            "trust_route_alert": evidence["trust_alerts"]["trust_route_alert"],
        })

    write_jsonl(args.out_dir / "evidence/attack_explanation_cases.jsonl", evidence_rows)
    write_csv(args.out_dir / "evidence/case_index.csv", index_rows)
    write_jsonl(args.out_dir / "prompts/explanation_requests.jsonl", prompt_rows)
    write_jsonl(args.out_dir / "evaluation/evaluation_cases.jsonl", evaluation_rows)
    write_jsonl(args.out_dir / "evaluation/handcrafted_schema_fixture.jsonl", fixture_rows)
    print(f"Wrote {len(evidence_rows)} LLM explanation cases to {args.out_dir}")


if __name__ == "__main__":
    main()

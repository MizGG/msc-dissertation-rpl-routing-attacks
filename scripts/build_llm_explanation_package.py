#!/usr/bin/env python3
"""Build label-free LLM explanation requests from verified IDS drift evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


EXPLANATION_FEATURES = (
    "state_nonroot_rank_min",
    "state_low_rank_nonroot_pairs",
    "state_low_rank_nonroot_senders",
    "state_receivers_exposed_low_rank_nonroot",
    "dio_rx_low_rank_nonroot_count",
    "dio_rx_count",
    "parent_switch_count",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> int | float:
    parsed = float(value or 0)
    return int(parsed) if parsed.is_integer() else parsed


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def find_one(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    matches = [row for row in rows if all(row.get(key) == value for key, value in criteria.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {criteria}; found {len(matches)}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-dir", type=Path, default=Path("experiments/routing_features_v1"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/llm_explanations"))
    args = parser.parse_args()

    features = read_csv(args.experiment_dir / "features/routing_window_features.csv")
    traces = read_csv(args.experiment_dir / "results/drift_detector_window_trace.csv")
    static_results = read_csv(args.experiment_dir / "results/static_results.csv")
    adaptation = read_csv(args.experiment_dir / "results/adaptation_summary.csv")

    static = find_one(
        static_results,
        experiment="static_blackhole_to_sinkhole",
        model="cart",
        feature_set="coarse_plus_routing",
    )
    adapted = find_one(
        adaptation,
        model="cart",
        feature_set="coarse_plus_routing",
        adaptation_sinkhole_seeds="3",
    )

    first_alarm_by_run: dict[str, dict[str, str]] = {}
    for row in traces:
        if row["alarm"] == "1" and row["evaluation_window_label"] == "1":
            first_alarm_by_run.setdefault(row["run_id"], row)

    alerts: list[dict[str, object]] = []
    requests: list[dict[str, object]] = []
    evaluations: list[dict[str, object]] = []
    reference_outputs: list[dict[str, object]] = []
    for run_id, trace in sorted(first_alarm_by_run.items()):
        seed = trace["seed"]
        window_start = trace["window_start_s"]
        observed = find_one(features, run_id=run_id, window_start_s=window_start)
        reference = find_one(
            features,
            family="sinkhole",
            mode="control",
            seed=seed,
            window_start_s=window_start,
        )
        alert_id = f"rpl-drift-{seed}-{window_start}"
        observations = {feature: number(observed[feature]) for feature in EXPLANATION_FEATURES}
        references = {feature: number(reference[feature]) for feature in EXPLANATION_FEATURES}
        evidence = {
            "alert_id": alert_id,
            "window": {"start_s": int(window_start), "end_s": int(trace["window_end_s"])},
            "detector": {
                "name": "one-sided CUSUM over persistent low-rank RPL state",
                "score": number(trace["rank_state_score"]),
                "cusum": number(trace["cusum"]),
                "decision_limit": number(trace["decision_limit"]),
            },
            "observed_routing_state": observations,
            "matched_reference_state": references,
            "ids_context": {
                "static_model_attack_recall": number(static["recall"]),
                "adapted_model_mean_recall": number(adapted["mean_recall"]),
                "adapted_model_mean_f1": number(adapted["mean_f1"]),
                "adapted_model_mean_fpr": number(adapted["mean_fpr"]),
            },
        }
        alerts.append(evidence)

        system = (
            "You are explaining an RPL intrusion-detection alert to a security analyst. "
            "Use only the supplied evidence. Distinguish observation from inference, do not invent node identities, "
            "packet loss, or topology changes, and describe an attack mechanism as likely rather than proven. "
            "Return valid JSON with keys summary, observed_change, likely_mechanism, confidence, limitations, "
            "and recommended_action. confidence must be one of low, medium, or high."
        )
        requests.append({
            "alert_id": alert_id,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(evidence, sort_keys=True)},
            ],
        })
        evaluations.append({
            "alert_id": alert_id,
            "ground_truth_for_evaluation_only": "controlled sinkhole rank-manipulation window",
            "required_facts": [
                f"non-root rank minimum changed from {references['state_nonroot_rank_min']} to {observations['state_nonroot_rank_min']}",
                f"low-rank state covered {observations['state_low_rank_nonroot_pairs']} receiver/sender pairs",
                f"CUSUM {number(trace['cusum'])} exceeded decision limit {number(trace['decision_limit'])}",
            ],
            "acceptable_inference": "likely rank manipulation or sinkhole-like parent attraction",
            "forbidden_unsupported_claims": [
                "a specific node is compromised",
                "packet dropping was observed",
                "the entire topology changed",
                "the attack identity is proven with certainty",
            ],
            "scoring": {
                "evidence_fidelity": "0-2",
                "mechanism_alignment": "0-2",
                "uncertainty_calibration": "0-2",
                "actionability": "0-2",
                "maximum_total": 8,
            },
        })
        reference_outputs.append({
            "alert_id": alert_id,
            "response": {
                "summary": (
                    f"Persistent low-rank RPL state raised a CUSUM alert in the "
                    f"{window_start}-{trace['window_end_s']} second window."
                ),
                "observed_change": (
                    f"The minimum observed non-root rank changed from {references['state_nonroot_rank_min']} "
                    f"in the matched reference to {observations['state_nonroot_rank_min']}. "
                    f"The state included {observations['state_low_rank_nonroot_pairs']} low-rank "
                    f"receiver/sender pairs, and CUSUM {number(trace['cusum'])} exceeded the "
                    f"decision limit {number(trace['decision_limit'])}."
                ),
                "likely_mechanism": (
                    "This is consistent with likely RPL rank manipulation or sinkhole-like parent attraction."
                ),
                "confidence": "high",
                "limitations": (
                    "The evidence identifies an anomalous routing advertisement pattern, not a proven attack "
                    "identity or a specific compromised node."
                ),
                "recommended_action": (
                    "Inspect the low-rank advertiser and verify parent changes before isolating any node."
                ),
            },
        })

    if len(alerts) != 5:
        raise ValueError(f"Expected five held-out sinkhole alert cases; found {len(alerts)}")

    write_jsonl(args.out_dir / "evidence/alerts.jsonl", alerts)
    write_jsonl(args.out_dir / "prompts/explanation_requests.jsonl", requests)
    write_jsonl(args.out_dir / "evaluation/evaluation_cases.jsonl", evaluations)
    write_jsonl(args.out_dir / "evaluation/handcrafted_schema_fixture.jsonl", reference_outputs)
    print(f"Wrote {len(alerts)} explanation cases to {args.out_dir}")


if __name__ == "__main__":
    main()

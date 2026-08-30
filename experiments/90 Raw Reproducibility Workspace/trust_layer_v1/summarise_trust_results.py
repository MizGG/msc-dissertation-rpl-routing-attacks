#!/usr/bin/env python3
"""Summarise trust-layer drift and adaptation results."""

from __future__ import annotations

import csv
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mean(values: list[float]) -> float:
    return round(statistics.mean(values), 4) if values else 0.0


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    drift = read(ROOT / "results/static_drift/cross_attack_matrix.csv")
    adapt = read(ROOT / "results/adaptation/cross_attack_adaptation_summary.csv")
    trust_features = read(ROOT / "features/trust_routing_window_features.csv")

    rows: list[dict[str, object]] = []
    for model in ("cart", "gaussian"):
        cross = [row for row in drift if row["model"] == model and row["evaluation"] == "cross_attack"]
        rows.append({
            "experiment": "trust_static_cross_attack",
            "model": model,
            "cross_attack_pairs": len(cross),
            "zero_recall_pairs": sum(1 for row in cross if float(row["recall"]) == 0),
            "strong_f1_ge_0_8_pairs": sum(1 for row in cross if float(row["f1"]) >= 0.8),
            "mean_recall": mean([float(row["recall"]) for row in cross]),
            "mean_f1": mean([float(row["f1"]) for row in cross]),
        })

    by_family: list[dict[str, object]] = []
    for family in sorted({row["family"] for row in trust_features}):
        for mode in ("control", "attack"):
            subset = [row for row in trust_features if row["family"] == family and row["mode"] == mode]
            post = [row for row in subset if int(row["window_start_s"]) >= 240]
            by_family.append({
                "family": family,
                "mode": mode,
                "post_activation_windows": len(post),
                "mean_trust_forwarding": mean([float(row["trust_forwarding"]) for row in post]),
                "mean_trust_rank": mean([float(row["trust_rank"]) for row in post]),
                "mean_trust_control": mean([float(row["trust_control"]) for row in post]),
                "mean_trust_route": mean([float(row["trust_route"]) for row in post]),
                "mean_trust_total": mean([float(row["trust_total"]) for row in post]),
                "penalised_windows": sum(1 for row in post if row["trust_penalised"] == "1"),
                "forwarding_alert_windows": sum(1 for row in post if row["trust_forwarding_alert"] == "1"),
                "rank_alert_windows": sum(1 for row in post if row["trust_rank_alert"] == "1"),
                "control_alert_windows": sum(1 for row in post if row["trust_control_alert"] == "1"),
                "route_alert_windows": sum(1 for row in post if row["trust_route_alert"] == "1"),
                "any_alert_windows": sum(1 for row in post if row["trust_any_alert"] == "1"),
            })

    adaptation_rows: list[dict[str, object]] = []
    for count in range(4):
        subset = [row for row in adapt if int(row["adaptation_seed_count"]) == count]
        adaptation_rows.append({
            "adaptation_seed_count": count,
            "pairs": len(subset),
            "mean_accuracy": mean([float(row["mean_accuracy"]) for row in subset]),
            "mean_precision": mean([float(row["mean_precision"]) for row in subset]),
            "mean_recall": mean([float(row["mean_recall"]) for row in subset]),
            "mean_f1": mean([float(row["mean_f1"]) for row in subset]),
            "mean_fpr": mean([float(row["mean_fpr"]) for row in subset]),
        })

    write_csv(ROOT / "results/trust_static_summary.csv", rows)
    write_csv(ROOT / "results/trust_by_family_summary.csv", by_family)
    write_csv(ROOT / "results/trust_adaptation_summary.csv", adaptation_rows)

    note = [
        "# Trust Layer V1 Results",
        "",
        "This is an offline trust-aware representation, not yet an online RPL",
        "defence. It tests whether trust-derived features add useful information",
        "for concept drift and adaptation.",
        "",
        "## Static Drift",
        "",
    ]
    for row in rows:
        note.append(
            f"- {row['model']}: zero recall {row['zero_recall_pairs']}/"
            f"{row['cross_attack_pairs']}, mean recall {row['mean_recall']}, "
            f"mean F1 {row['mean_f1']}."
        )
    note.extend([
        "",
        "## Adaptation",
        "",
    ])
    for row in adaptation_rows:
        note.append(
            f"- {row['adaptation_seed_count']} target seeds: mean recall "
            f"{row['mean_recall']}, mean F1 {row['mean_f1']}."
        )
    note.extend([
        "",
        "## Interpretation",
        "",
        "The trust layer is strongest for forwarding-style attacks and useful as a",
        "diagnostic feature representation. It should not be claimed as a complete",
        "defence against Sybil or wormhole attacks, because those attacks can require",
        "identity binding, topology plausibility or timing evidence beyond simple",
        "forwarding trust.",
    ])
    (ROOT / "results/trust_layer_interpretation.md").write_text("\n".join(note) + "\n", encoding="utf-8")
    print("Wrote trust-layer summaries")


if __name__ == "__main__":
    main()

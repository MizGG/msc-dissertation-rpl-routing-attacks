#!/usr/bin/env python3
"""Summarise seed-level spread without treating overlapping splits as independent."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson interval for complete-run detection/false-alarm proportions."""
    if total == 0:
        return 0.0, 0.0
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((proportion * (1 - proportion) + z * z / (4 * total)) / total) / denominator
    return centre - margin, centre + margin


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--adaptation",
        type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/routing_features_v1/results/adaptation_curve.csv"),
    )
    parser.add_argument(
        "--detectors",
        type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/online_drift_response_v1/results/detector_comparison_summary.csv"),
    )
    parser.add_argument(
        "--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/dissertation_robustness_v1/results")
    )
    args = parser.parse_args()

    adaptation = [
        row for row in read_csv(args.adaptation)
        if row["model"] == "cart" and row["feature_set"] == "coarse_plus_routing"
    ]
    spread: list[dict[str, object]] = []
    for count in range(4):
        rows = [row for row in adaptation if int(row["adaptation_sinkhole_seeds"]) == count]
        for metric in ("accuracy", "precision", "recall", "f1", "fpr"):
            values = [float(row[metric]) for row in rows]
            spread.append({
                "experiment": "blackhole_to_sinkhole_routing_cart_adaptation",
                "adaptation_sinkhole_seeds": count,
                "metric": metric,
                "split_count": len(values),
                "mean": round(statistics.mean(values), 4),
                "standard_deviation": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
                "minimum": round(min(values), 4),
                "maximum": round(max(values), 4),
                "interpretation": "spread across overlapping whole-seed adaptation/evaluation splits; not an independent confidence interval",
            })

    detector_rows = read_csv(args.detectors)
    detector_uncertainty: list[dict[str, object]] = []
    for row in detector_rows:
        attacks = int(row["attack_runs"])
        detected = int(row["detected_without_prealarm"])
        controls = int(row["control_runs"])
        false_alarms = int(row["control_false_alarms"])
        detect_low, detect_high = wilson_interval(detected, attacks)
        false_low, false_high = wilson_interval(false_alarms, controls)
        detector_uncertainty.append({
            "detector": row["detector"],
            "attack_detection_rate": row["attack_detection_rate"],
            "attack_runs": attacks,
            "detection_wilson_95_lower": round(detect_low, 4),
            "detection_wilson_95_upper": round(detect_high, 4),
            "control_false_alarm_rate": row["control_false_alarm_rate"],
            "control_runs": controls,
            "false_alarm_wilson_95_lower": round(false_low, 4),
            "false_alarm_wilson_95_upper": round(false_high, 4),
            "interpretation": "run-level Wilson interval over five attack and five control seeds; wide intervals reflect the small Cooja campaign",
        })

    write_csv(args.out_dir / "adaptation_seed_spread.csv", spread)
    write_csv(args.out_dir / "detector_rate_uncertainty.csv", detector_uncertainty)
    print(f"Wrote uncertainty summaries to {args.out_dir}")


if __name__ == "__main__":
    main()

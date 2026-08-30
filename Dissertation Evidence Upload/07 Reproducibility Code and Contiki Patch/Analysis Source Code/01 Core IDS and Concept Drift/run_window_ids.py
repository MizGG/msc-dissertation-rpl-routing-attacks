#!/usr/bin/env python3
"""Window-level IDS experiments for controlled attack-distribution change."""

from __future__ import annotations

import argparse
import csv
import math
from itertools import combinations
from pathlib import Path

from run_baseline_ids import metrics


FEATURES = [
    "app_tx_delta",
    "app_rx_delta",
    "app_missed_delta",
    "app_reporting_nodes",
    "parent_found_events",
    "no_parent_events",
    "radio_tx_count",
    "radio_bytes",
    "radio_interfered_count",
    "unique_radio_senders",
    "attacker_node16_radio_tx",
    "root_node1_radio_tx",
]


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["binary_label"] = row["window_label"]
    return rows


def evaluate(name: str, train: list[dict[str, str]], test: list[dict[str, str]]) -> dict[str, str | int | float]:
    classes = sorted({int(row["binary_label"]) for row in train})
    means: dict[int, list[float]] = {}
    variances: dict[int, list[float]] = {}
    priors: dict[int, float] = {}
    for label in classes:
        class_rows = [row for row in train if int(row["binary_label"]) == label]
        priors[label] = len(class_rows) / len(train)
        class_values = [[float(row[feature] or 0) for feature in FEATURES] for row in class_rows]
        means[label] = [sum(values[idx] for values in class_values) / len(class_values) for idx in range(len(FEATURES))]
        variances[label] = []
        for idx, mean in enumerate(means[label]):
            variance = sum((values[idx] - mean) ** 2 for values in class_values) / max(1, len(class_values) - 1)
            variances[label].append(max(variance, 1e-6))

    predictions: list[int] = []
    for row in test:
        values = [float(row[feature] or 0) for feature in FEATURES]
        best_label = 0
        best_score = -float("inf")
        for label in classes:
            score = math.log(priors[label])
            for value, mean, variance in zip(values, means[label], variances[label]):
                score += -0.5 * math.log(2 * math.pi * variance) - ((value - mean) ** 2 / (2 * variance))
            if score > best_score:
                best_label = label
                best_score = score
        predictions.append(best_label)
    return {"experiment": name, "train_windows": len(train), **metrics(test, predictions)}


def write_csv(path: Path, rows: list[dict[str, str | int | float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/features/window_features.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/ml_window"))
    args = parser.parse_args()

    rows = load_rows(args.features)
    blackhole = [row for row in rows if row["family"] == "blackhole"]
    sinkhole = [row for row in rows if row["family"] == "sinkhole"]

    results: list[dict[str, str | int | float]] = []
    for seed in sorted({row["seed"] for row in blackhole}):
        train = [row for row in blackhole if row["seed"] != seed]
        test = [row for row in blackhole if row["seed"] == seed]
        results.append(evaluate(f"blackhole_window_leave_seed_{seed}", train, test))

    results.append(evaluate("window_drift_train_blackhole_test_sinkhole", blackhole, sinkhole))

    adaptation_rows: list[dict[str, str | int | float]] = []
    sinkhole_seeds = sorted({row["seed"] for row in sinkhole})
    adaptation_rows.append({
        **evaluate("window_adapt_0_static_blackhole_only", blackhole, sinkhole),
        "adaptation_sinkhole_seeds": 0,
        "adaptation_windows": 0,
        "adaptation_seeds": "",
        "test_seeds": ",".join(sinkhole_seeds),
    })
    for count in range(1, min(3, len(sinkhole_seeds) - 1) + 1):
        for seed_tuple in combinations(sinkhole_seeds, count):
            adaptation_seed_set = set(seed_tuple)
            train = blackhole + [row for row in sinkhole if row["seed"] in adaptation_seed_set]
            test = [row for row in sinkhole if row["seed"] not in adaptation_seed_set]
            adaptation_rows.append({
                **evaluate(f"window_adapt_{count}_sinkhole_seed_combo", train, test),
                "adaptation_sinkhole_seeds": count,
                "adaptation_windows": len(train) - len(blackhole),
                "adaptation_seeds": ",".join(seed_tuple),
                "test_seeds": ",".join(seed for seed in sinkhole_seeds if seed not in adaptation_seed_set),
            })

    summary: list[dict[str, str | int | float]] = []
    for count in sorted({int(row["adaptation_sinkhole_seeds"]) for row in adaptation_rows}):
        group = [row for row in adaptation_rows if int(row["adaptation_sinkhole_seeds"]) == count]
        summary.append({
            "adaptation_sinkhole_seeds": count,
            "splits": len(group),
            "mean_accuracy": round(sum(float(row["accuracy"]) for row in group) / len(group), 4),
            "mean_precision": round(sum(float(row["precision"]) for row in group) / len(group), 4),
            "mean_recall": round(sum(float(row["recall"]) for row in group) / len(group), 4),
            "mean_f1": round(sum(float(row["f1"]) for row in group) / len(group), 4),
            "mean_f2": round(sum(float(row["f2"]) for row in group) / len(group), 4),
            "mean_fpr": round(sum(float(row["fpr"]) for row in group) / len(group), 4),
        })

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "window_results.csv", results)
    write_csv(args.out_dir / "window_adaptation_curve.csv", adaptation_rows)
    write_csv(args.out_dir / "window_adaptation_summary.csv", summary)
    (args.out_dir / "README.md").write_text(
        "# Window-Level IDS Results\n\n"
        "Uses 60-second windows from final blackhole and sinkhole Cooja runs. "
        "Model features exclude explicit attack-marker columns such as sinkhole "
        "advertised-rank events and blackhole drop logs.\n\n"
        "Labels mark attack-run windows at or after the 240-second activation time "
        "as attack; earlier attack-run windows and all control windows are normal.\n",
        encoding="utf-8",
    )
    print(args.out_dir / "window_results.csv")
    print(args.out_dir / "window_adaptation_summary.csv")


if __name__ == "__main__":
    main()

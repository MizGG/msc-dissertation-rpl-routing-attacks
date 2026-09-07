#!/usr/bin/env python3
"""Evaluate coarse and routing-aware IDS features under whole-seed drift."""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from itertools import combinations
from pathlib import Path

from run_baseline_ids import metrics


COARSE_FEATURES = [
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

ROUTING_FEATURES = [
    "dio_rx_count",
    "dio_tx_count",
    "dis_rx_count",
    "dis_tx_count",
    "dao_rx_count",
    "dao_tx_count",
    "parent_switch_count",
    "parent_switch_to_root_count",
    "parent_switch_to_nonroot_count",
    "unique_parent_targets",
    "significant_rank_update_count",
    "unique_dio_senders",
    "unique_dio_receivers",
    "dio_rx_rank_min",
    "dio_rx_rank_mean",
    "dio_rx_rank_max",
    "dio_rx_rank_range",
    "dio_rx_nonroot_count",
    "dio_rx_nonroot_rank_min",
    "dio_rx_nonroot_rank_mean",
    "dio_rx_nonroot_rank_max",
    "dio_rx_nonroot_rank_range",
    "dio_rx_low_rank_nonroot_count",
    "unique_low_rank_nonroot_senders",
    "dio_tx_rank_mean",
    "state_nonroot_rank_min",
    "state_nonroot_rank_mean",
    "state_nonroot_rank_max",
    "state_nonroot_rank_range",
    "state_low_rank_nonroot_pairs",
    "state_low_rank_nonroot_senders",
    "state_receivers_exposed_low_rank_nonroot",
    "own_state_sample_count",
    "own_rank_min",
    "own_rank_mean",
    "own_rank_max",
    "own_rank_range",
    "own_neighbor_count_mean",
    "own_neighbor_count_max",
    "topology_edge_count",
    "topology_unique_parents",
    "topology_max_parent_fanout",
    "topology_root_direct_children",
    "topology_mean_depth",
    "topology_max_depth",
]

FEATURE_SETS = {
    "coarse": COARSE_FEATURES,
    "coarse_plus_routing": COARSE_FEATURES + ROUTING_FEATURES,
}
MODEL_NAMES = ("gaussian", "cart")


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["binary_label"] = row["window_label"]
    return rows


class GaussianClassifier:
    def __init__(self, features: list[str]) -> None:
        self.features = features
        self.classes: list[int] = []
        self.means: dict[int, list[float]] = {}
        self.variances: dict[int, list[float]] = {}
        self.priors: dict[int, float] = {}

    def values(self, row: dict[str, str]) -> list[float]:
        return [float(row[feature] or 0) for feature in self.features]

    def fit(self, rows: list[dict[str, str]]) -> None:
        self.classes = sorted({int(row["binary_label"]) for row in rows})
        for label in self.classes:
            class_rows = [row for row in rows if int(row["binary_label"]) == label]
            values = [self.values(row) for row in class_rows]
            self.priors[label] = len(class_rows) / len(rows)
            self.means[label] = [sum(row[idx] for row in values) / len(values) for idx in range(len(self.features))]
            self.variances[label] = []
            for idx, mean in enumerate(self.means[label]):
                variance = sum((row[idx] - mean) ** 2 for row in values) / max(1, len(values) - 1)
                self.variances[label].append(max(variance, 1e-6))

    def predict_one(self, row: dict[str, str]) -> int:
        values = self.values(row)
        best_label = 0
        best_score = -float("inf")
        for label in self.classes:
            score = math.log(self.priors[label])
            for value, mean, variance in zip(values, self.means[label], self.variances[label]):
                score += -0.5 * math.log(2 * math.pi * variance) - (value - mean) ** 2 / (2 * variance)
            if score > best_score:
                best_label = label
                best_score = score
        return best_label

    def predict(self, rows: list[dict[str, str]]) -> list[int]:
        return [self.predict_one(row) for row in rows]


def gini(labels: list[int]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    return 1.0 - sum((count / len(labels)) ** 2 for count in counts.values())


class CartClassifier:
    def __init__(self, features: list[str], max_depth: int = 4, min_leaf: int = 2) -> None:
        self.features = features
        self.max_depth = max_depth
        self.min_leaf = min_leaf
        self.root: dict[str, object] | None = None

    def value(self, row: dict[str, str], feature: str) -> float:
        return float(row[feature] or 0)

    def fit(self, rows: list[dict[str, str]]) -> None:
        self.root = self.build(rows, 0)

    def build(self, rows: list[dict[str, str]], depth: int) -> dict[str, object]:
        labels = [int(row["binary_label"]) for row in rows]
        majority = Counter(labels).most_common(1)[0][0]
        if depth >= self.max_depth or len(set(labels)) == 1 or len(rows) < self.min_leaf * 2:
            return {"leaf": majority}
        parent_impurity = gini(labels)
        best: tuple[float, str, float, list[dict[str, str]], list[dict[str, str]]] | None = None
        for feature in self.features:
            values = sorted({self.value(row, feature) for row in rows})
            for left_value, right_value in zip(values, values[1:]):
                threshold = (left_value + right_value) / 2
                left = [row for row in rows if self.value(row, feature) <= threshold]
                right = [row for row in rows if self.value(row, feature) > threshold]
                if len(left) < self.min_leaf or len(right) < self.min_leaf:
                    continue
                impurity = (len(left) * gini([int(row["binary_label"]) for row in left])
                            + len(right) * gini([int(row["binary_label"]) for row in right])) / len(rows)
                gain = parent_impurity - impurity
                if best is None or gain > best[0]:
                    best = (gain, feature, threshold, left, right)
        if best is None or best[0] <= 0:
            return {"leaf": majority}
        _, feature, threshold, left, right = best
        return {
            "feature": feature,
            "threshold": threshold,
            "left": self.build(left, depth + 1),
            "right": self.build(right, depth + 1),
        }

    def predict_one(self, row: dict[str, str]) -> int:
        node = self.root
        while node is not None and "leaf" not in node:
            branch = "left" if self.value(row, str(node["feature"])) <= float(node["threshold"]) else "right"
            node = node[branch]  # type: ignore[assignment]
        return int(node["leaf"]) if node is not None else 0

    def predict(self, rows: list[dict[str, str]]) -> list[int]:
        return [self.predict_one(row) for row in rows]


def evaluate(
    name: str,
    model_name: str,
    feature_set: str,
    train: list[dict[str, str]],
    test: list[dict[str, str]],
) -> dict[str, object]:
    features = FEATURE_SETS[feature_set]
    model = GaussianClassifier(features) if model_name == "gaussian" else CartClassifier(features)
    model.fit(train)
    return {
        "experiment": name,
        "model": model_name,
        "feature_set": feature_set,
        "train_windows": len(train),
        **metrics(test, model.predict(test)),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/routing_features_v1/features/routing_window_features.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/routing_features_v1/results"))
    args = parser.parse_args()

    rows = load_rows(args.features)
    blackhole = [row for row in rows if row["family"] == "blackhole"]
    sinkhole = [row for row in rows if row["family"] == "sinkhole"]
    sinkhole_seeds = sorted({row["seed"] for row in sinkhole})
    static_rows: list[dict[str, object]] = []
    adaptation_rows: list[dict[str, object]] = []

    for model_name in MODEL_NAMES:
        for feature_set in FEATURE_SETS:
            for seed in sorted({row["seed"] for row in blackhole}):
                train = [row for row in blackhole if row["seed"] != seed]
                test = [row for row in blackhole if row["seed"] == seed]
                static_rows.append(evaluate(f"blackhole_leave_seed_{seed}", model_name, feature_set, train, test))
            static_rows.append(evaluate("static_blackhole_to_sinkhole", model_name, feature_set, blackhole, sinkhole))

            for count in range(0, 4):
                seed_combinations = [()] if count == 0 else combinations(sinkhole_seeds, count)
                for selected in seed_combinations:
                    selected_set = set(selected)
                    adaptation = [row for row in sinkhole if row["seed"] in selected_set]
                    test = sinkhole if count == 0 else [row for row in sinkhole if row["seed"] not in selected_set]
                    adaptation_rows.append({
                        **evaluate(
                            f"adapt_{count}_sinkhole_seeds",
                            model_name,
                            feature_set,
                            blackhole + adaptation,
                            test,
                        ),
                        "adaptation_sinkhole_seeds": count,
                        "adaptation_windows": len(adaptation),
                        "adaptation_seeds": ",".join(selected),
                        "test_seeds": ",".join(seed for seed in sinkhole_seeds if seed not in selected_set),
                    })

    summary: list[dict[str, object]] = []
    for model_name in MODEL_NAMES:
        for feature_set in FEATURE_SETS:
            for count in range(0, 4):
                group = [
                    row for row in adaptation_rows
                    if row["model"] == model_name
                    and row["feature_set"] == feature_set
                    and row["adaptation_sinkhole_seeds"] == count
                ]
                summary.append({
                    "model": model_name,
                    "feature_set": feature_set,
                    "adaptation_sinkhole_seeds": count,
                    "splits": len(group),
                    "mean_accuracy": round(sum(float(row["accuracy"]) for row in group) / len(group), 4),
                    "mean_precision": round(sum(float(row["precision"]) for row in group) / len(group), 4),
                    "mean_recall": round(sum(float(row["recall"]) for row in group) / len(group), 4),
                    "mean_f1": round(sum(float(row["f1"]) for row in group) / len(group), 4),
                    "mean_f2": round(sum(float(row["f2"]) for row in group) / len(group), 4),
                    "mean_fpr": round(sum(float(row["fpr"]) for row in group) / len(group), 4),
                })

    post_sinkhole = [row for row in sinkhole if int(row["post_activation"]) == 1]
    diagnostics: list[dict[str, object]] = []
    for feature in ROUTING_FEATURES:
        attack = [float(row[feature] or 0) for row in post_sinkhole if row["mode"] == "attack"]
        control = [float(row[feature] or 0) for row in post_sinkhole if row["mode"] == "control"]
        attack_mean = sum(attack) / len(attack)
        control_mean = sum(control) / len(control)
        diagnostics.append({
            "feature": feature,
            "sinkhole_attack_post_mean": round(attack_mean, 4),
            "sinkhole_control_post_mean": round(control_mean, 4),
            "difference": round(attack_mean - control_mean, 4),
        })

    write_csv(args.out_dir / "static_results.csv", static_rows)
    write_csv(args.out_dir / "adaptation_curve.csv", adaptation_rows)
    write_csv(args.out_dir / "adaptation_summary.csv", summary)
    write_csv(args.out_dir / "routing_feature_diagnostics.csv", diagnostics)
    print(f"Wrote routing IDS results to {args.out_dir}")


if __name__ == "__main__":
    main()

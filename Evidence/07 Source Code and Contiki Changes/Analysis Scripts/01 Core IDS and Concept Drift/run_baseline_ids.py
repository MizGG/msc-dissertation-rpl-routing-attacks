#!/usr/bin/env python3
"""Pure-Python baseline IDS experiments for the dissertation pipeline.

This avoids external ML dependencies and keeps the first concept-drift result
reproducible on the current machine. The model is a small random forest of
numeric decision trees trained on complete simulation runs.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from collections import Counter
from itertools import combinations
from pathlib import Path


FEATURES = [
    "app_received_requests",
    "app_received_responses",
    "app_not_reachable",
    "app_tx_stat_lines",
    "radio_count_reported",
    "radio_transmissions",
    "testlog_lines",
    "radio_lines",
]


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def x(row: dict[str, str]) -> list[float]:
    return [float(row[name] or 0) for name in FEATURES]


def y(row: dict[str, str]) -> int:
    return int(row["binary_label"])


def gini(labels: list[int]) -> float:
    total = len(labels)
    if total == 0:
        return 0.0
    counts = Counter(labels)
    return 1.0 - sum((count / total) ** 2 for count in counts.values())


class Tree:
    def __init__(self, max_depth: int = 3, min_leaf: int = 1, mtry: int | None = None):
        self.max_depth = max_depth
        self.min_leaf = min_leaf
        self.mtry = mtry
        self.node = None

    def fit(self, rows: list[dict[str, str]], rng: random.Random) -> None:
        self.node = self._build(rows, 0, rng)

    def _build(self, rows: list[dict[str, str]], depth: int, rng: random.Random):
        labels = [y(row) for row in rows]
        majority = Counter(labels).most_common(1)[0][0]
        if depth >= self.max_depth or len(set(labels)) == 1 or len(rows) <= self.min_leaf * 2:
            return {"leaf": majority}

        feature_indexes = list(range(len(FEATURES)))
        rng.shuffle(feature_indexes)
        feature_indexes = feature_indexes[: self.mtry or len(FEATURES)]

        best = None
        parent_impurity = gini(labels)
        for idx in feature_indexes:
            values = sorted(set(x(row)[idx] for row in rows))
            if len(values) < 2:
                continue
            thresholds = [(a + b) / 2 for a, b in zip(values, values[1:])]
            for threshold in thresholds:
                left = [row for row in rows if x(row)[idx] <= threshold]
                right = [row for row in rows if x(row)[idx] > threshold]
                if len(left) < self.min_leaf or len(right) < self.min_leaf:
                    continue
                impurity = (len(left) * gini([y(r) for r in left]) + len(right) * gini([y(r) for r in right])) / len(rows)
                gain = parent_impurity - impurity
                if best is None or gain > best[0]:
                    best = (gain, idx, threshold, left, right)

        if best is None or best[0] <= 0:
            return {"leaf": majority}

        _, idx, threshold, left, right = best
        return {
            "feature": idx,
            "threshold": threshold,
            "left": self._build(left, depth + 1, rng),
            "right": self._build(right, depth + 1, rng),
            "fallback": majority,
        }

    def predict_one(self, row: dict[str, str]) -> int:
        node = self.node
        while node is not None and "leaf" not in node:
            node = node["left"] if x(row)[node["feature"]] <= node["threshold"] else node["right"]
        return int(node["leaf"]) if node is not None else 0


class Forest:
    def __init__(self, n_trees: int = 101, max_depth: int = 3, seed: int = 7):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.seed = seed
        self.trees: list[Tree] = []

    def fit(self, rows: list[dict[str, str]]) -> None:
        rng = random.Random(self.seed)
        self.trees = []
        mtry = max(1, int(math.sqrt(len(FEATURES))))
        for _ in range(self.n_trees):
            sample = [rng.choice(rows) for _ in rows]
            tree = Tree(max_depth=self.max_depth, min_leaf=1, mtry=mtry)
            tree.fit(sample, rng)
            self.trees.append(tree)

    def predict_one(self, row: dict[str, str]) -> int:
        votes = [tree.predict_one(row) for tree in self.trees]
        return Counter(votes).most_common(1)[0][0]

    def predict(self, rows: list[dict[str, str]]) -> list[int]:
        return [self.predict_one(row) for row in rows]


def metrics(rows: list[dict[str, str]], preds: list[int]) -> dict[str, float | int]:
    labels = [y(row) for row in rows]
    tp = sum(1 for truth, pred in zip(labels, preds) if truth == 1 and pred == 1)
    tn = sum(1 for truth, pred in zip(labels, preds) if truth == 0 and pred == 0)
    fp = sum(1 for truth, pred in zip(labels, preds) if truth == 0 and pred == 1)
    fn = sum(1 for truth, pred in zip(labels, preds) if truth == 1 and pred == 0)
    accuracy = (tp + tn) / len(rows) if rows else 0
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    f2 = 5 * precision * recall / ((4 * precision) + recall) if (4 * precision) + recall else 0
    fpr = fp / (fp + tn) if fp + tn else 0
    return {
        "n": len(rows),
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "f2": round(f2, 4),
        "fpr": round(fpr, 4),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def evaluate(name: str, train: list[dict[str, str]], test: list[dict[str, str]]) -> dict[str, str | float | int]:
    model = Forest()
    model.fit(train)
    result = metrics(test, model.predict(test))
    return {"experiment": name, "train_runs": len(train), **result}


def evaluate_adaptation_curve(blackhole: list[dict[str, str]], sinkhole: list[dict[str, str]]) -> list[dict[str, str | float | int]]:
    sinkhole_seeds = sorted({row["seed"] for row in sinkhole})
    results: list[dict[str, str | float | int]] = []

    static = evaluate("adapt_0_static_blackhole_only", blackhole, sinkhole)
    static.update({
        "adaptation_seed_count": 0,
        "adaptation_runs": 0,
        "adaptation_seeds": "",
        "test_seeds": ",".join(sinkhole_seeds),
    })
    results.append(static)

    max_adaptation_seeds = min(3, len(sinkhole_seeds) - 1)
    for adaptation_count in range(1, max_adaptation_seeds + 1):
        for adaptation_seeds_tuple in combinations(sinkhole_seeds, adaptation_count):
            adaptation_seeds = set(adaptation_seeds_tuple)
            adaptation_rows = [row for row in sinkhole if row["seed"] in adaptation_seeds]
            test_rows = [row for row in sinkhole if row["seed"] not in adaptation_seeds]
            result = evaluate(
                f"adapt_{adaptation_count}_sinkhole_seed_combo",
                blackhole + adaptation_rows,
                test_rows,
            )
            result.update({
                "adaptation_seed_count": adaptation_count,
                "adaptation_runs": len(adaptation_rows),
                "adaptation_seeds": ",".join(adaptation_seeds_tuple),
                "test_seeds": ",".join(seed for seed in sinkhole_seeds if seed not in adaptation_seeds),
            })
            results.append(result)

    return results


def summarise_adaptation(results: list[dict[str, str | float | int]]) -> list[dict[str, str | float | int]]:
    grouped: dict[int, list[dict[str, str | float | int]]] = {}
    for row in results:
        grouped.setdefault(int(row["adaptation_seed_count"]), []).append(row)

    summaries: list[dict[str, str | float | int]] = []
    for adaptation_seed_count, rows in sorted(grouped.items()):
        summaries.append({
            "adaptation_sinkhole_seeds": adaptation_seed_count,
            "adaptation_runs": int(rows[0]["adaptation_runs"]),
            "splits": len(rows),
            "mean_accuracy": round(sum(float(row["accuracy"]) for row in rows) / len(rows), 4),
            "mean_precision": round(sum(float(row["precision"]) for row in rows) / len(rows), 4),
            "mean_recall": round(sum(float(row["recall"]) for row in rows) / len(rows), 4),
            "mean_f1": round(sum(float(row["f1"]) for row in rows) / len(rows), 4),
        })
    return summaries


def feature_diagnostics(rows: list[dict[str, str]]) -> list[dict[str, str | float | int]]:
    diagnostics: list[dict[str, str | float | int]] = []
    for family in sorted({row["family"] for row in rows}):
        family_rows = [row for row in rows if row["family"] == family]
        attack_rows = [row for row in family_rows if row["mode"] == "attack"]
        control_rows = [row for row in family_rows if row["mode"] == "control"]
        for feature in FEATURES:
            attack_mean = sum(float(row[feature] or 0) for row in attack_rows) / len(attack_rows)
            control_mean = sum(float(row[feature] or 0) for row in control_rows) / len(control_rows)
            diagnostics.append({
                "family": family,
                "feature": feature,
                "attack_mean": round(attack_mean, 4),
                "control_mean": round(control_mean, 4),
                "difference": round(attack_mean - control_mean, 4),
            })
    return diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/features/run_level_features.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/ml_baseline"))
    args = parser.parse_args()

    rows = load_rows(args.features)
    blackhole = [row for row in rows if row["family"] == "blackhole"]
    sinkhole = [row for row in rows if row["family"] == "sinkhole"]

    results = []
    for seed in sorted({row["seed"] for row in blackhole}):
        train = [row for row in blackhole if row["seed"] != seed]
        test = [row for row in blackhole if row["seed"] == seed]
        results.append(evaluate(f"blackhole_leave_seed_{seed}", train, test))

    results.append(evaluate("same_distribution_blackhole_all_seen_shape", blackhole, blackhole))
    results.append(evaluate("concept_drift_train_blackhole_test_sinkhole", blackhole, sinkhole))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = args.out_dir / "baseline_results.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    adaptation_results = evaluate_adaptation_curve(blackhole, sinkhole)
    adaptation_csv = args.out_dir / "adaptation_curve.csv"
    with adaptation_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(adaptation_results[0].keys()))
        writer.writeheader()
        writer.writerows(adaptation_results)

    adaptation_summary = summarise_adaptation(adaptation_results)
    adaptation_summary_csv = args.out_dir / "adaptation_summary.csv"
    with adaptation_summary_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(adaptation_summary[0].keys()))
        writer.writeheader()
        writer.writerows(adaptation_summary)

    diagnostics = feature_diagnostics(rows)
    diagnostics_csv = args.out_dir / "feature_diagnostics.csv"
    with diagnostics_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(diagnostics[0].keys()))
        writer.writeheader()
        writer.writerows(diagnostics)

    notes = args.out_dir / "README.md"
    notes.write_text(
        "# Baseline IDS Results\n\n"
        "Pure-Python random forest over complete-run traffic features from "
        "`experiments/90 Raw Reproducibility Workspace/features/run_level_features.csv`.\n\n"
        "Attack-marker fields such as sinkhole advertised-rank events and blackhole "
        "log counts are excluded from training to avoid label leakage.\n\n"
        "The main drift row is `concept_drift_train_blackhole_test_sinkhole`: "
        "a model trained on blackhole/control runs is evaluated on sinkhole/control "
        "runs.\n\n"
        "`adaptation_curve.csv` and `adaptation_summary.csv` evaluate recovery after "
        "adding whole sinkhole seeds to the training set. Evaluation always uses "
        "sinkhole seeds that were not used for adaptation.\n\n"
        "`feature_diagnostics.csv` compares attack/control feature means by attack "
        "family and helps explain whether the run-level feature set captures each "
        "attack mechanism.\n",
        encoding="utf-8",
    )

    print(out_csv)
    print(adaptation_csv)
    print(adaptation_summary_csv)
    print(diagnostics_csv)


if __name__ == "__main__":
    main()

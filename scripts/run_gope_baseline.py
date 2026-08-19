#!/usr/bin/env python3
"""Preliminary baseline over the supplied Dr Gope labelled datasets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import random
from collections import defaultdict
from pathlib import Path

from audit_gope_dataset import normalise_attack
from run_baseline_ids import metrics


FEATURES = [
    "Source_Rank",
    "Parents_Count",
    "Parrent_Node",
    "Src_DIO_count",
    "Dst_DIO_count",
    "Src_DAO_count",
    "Dst_DAO_count",
    "Src_DIS_count",
    "Dst_DIS_count",
    "Src_host_count",
    "Dst_host_count",
    "Rcv_host_count",
    "Trp_app_count",
    "hop_count",
    "Avg_hop_count",
    "pkt_loss",
    "cpkt_loss",
    "same_parent",
    "RSSI(dbm)",
    "TX_RX_Distance",
]


def to_float(value: str) -> float:
    if value is None:
        return 0.0
    text = value.strip()
    if text == "" or text.lower() in {"nan", "na", "null", "none"}:
        return 0.0
    try:
        return float(text)
    except ValueError:
        # Python's built-in hash is process-randomised. A fixed digest keeps
        # categorical fallback values stable across reruns and machines.
        return float(int.from_bytes(hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest(), "big") % 10000)


def load_balanced_rows(dataset_dir: Path, max_per_class_per_attack: int, seed: int) -> list[dict[str, str]]:
    rng = random.Random(seed)
    rows: list[dict[str, str]] = []
    for path in sorted(dataset_dir.glob("*/*.csv")):
        with path.open(newline="", encoding="utf-8", errors="replace") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "TYPE" not in reader.fieldnames:
                continue
            buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
            for row in reader:
                label_text = row.get("TYPE", "")
                if label_text not in {"Normal", "Attack"}:
                    continue
                row["attack_family"] = normalise_attack(path)
                row["binary_label"] = "1" if label_text == "Attack" else "0"
                buckets[label_text].append(row)
            for label_rows in buckets.values():
                rng.shuffle(label_rows)
                rows.extend(label_rows[:max_per_class_per_attack])
    return rows


def split_by_attack(rows: list[dict[str, str]], test_fraction: float, seed: int) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rng = random.Random(seed)
    train: list[dict[str, str]] = []
    test: list[dict[str, str]] = []
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["attack_family"], row["binary_label"])].append(row)
    for group_rows in grouped.values():
        rng.shuffle(group_rows)
        cut = max(1, int(len(group_rows) * (1 - test_fraction)))
        train.extend(group_rows[:cut])
        test.extend(group_rows[cut:])
    return train, test


class GaussianBaseline:
    def __init__(self) -> None:
        self.classes: list[int] = []
        self.means: dict[int, list[float]] = {}
        self.variances: dict[int, list[float]] = {}
        self.priors: dict[int, float] = {}

    def fit(self, rows: list[dict[str, str]]) -> None:
        self.classes = sorted({int(row["binary_label"]) for row in rows})
        for label in self.classes:
            class_rows = [row for row in rows if int(row["binary_label"]) == label]
            self.priors[label] = len(class_rows) / len(rows)
            values = [[to_float(row.get(feature, "")) for feature in FEATURES] for row in class_rows]
            self.means[label] = [sum(row[idx] for row in values) / len(values) for idx in range(len(FEATURES))]
            self.variances[label] = []
            for idx, mean in enumerate(self.means[label]):
                variance = sum((row[idx] - mean) ** 2 for row in values) / max(1, len(values) - 1)
                self.variances[label].append(max(variance, 1e-6))

    def predict_one(self, row: dict[str, str]) -> int:
        values = [to_float(row.get(feature, "")) for feature in FEATURES]
        best_label = 0
        best_score = -float("inf")
        for label in self.classes:
            score = math.log(self.priors[label])
            for value, mean, variance in zip(values, self.means[label], self.variances[label]):
                score += -0.5 * math.log(2 * math.pi * variance) - ((value - mean) ** 2 / (2 * variance))
            if score > best_score:
                best_label = label
                best_score = score
        return best_label

    def predict(self, rows: list[dict[str, str]]) -> list[int]:
        return [self.predict_one(row) for row in rows]


def evaluate(name: str, train: list[dict[str, str]], test: list[dict[str, str]]) -> dict[str, str | int | float]:
    model = GaussianBaseline()
    model.fit(train)
    return {"experiment": name, "train_rows": len(train), **metrics(test, model.predict(test))}


def write_csv(path: Path, rows: list[dict[str, str | int | float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path("/Users/mizzy/Documents/Dissertation/Dissertation_Cooja_Work/DR P"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/gope_dataset"))
    parser.add_argument("--max-per-class-per-attack", type=int, default=5000)
    args = parser.parse_args()

    rows = load_balanced_rows(args.dataset_dir, args.max_per_class_per_attack, seed=17)
    train, test = split_by_attack(rows, test_fraction=0.3, seed=23)
    results = [evaluate("gope_balanced_routing_features_all_labelled_attacks", train, test)]

    blackhole = [row for row in rows if row["attack_family"] == "blackhole"]
    sinkhole = [row for row in rows if row["attack_family"] == "sinkhole"]
    if blackhole and sinkhole:
        results.append(evaluate("gope_train_blackhole_test_sinkhole", blackhole, sinkhole))

    write_csv(args.out_dir / "gope_baseline_results.csv", results)
    (args.out_dir / "gope_baseline_notes.md").write_text(
        "# Preliminary Gope Baseline\n\n"
        "This is a first reproducible supervised baseline over the seven labelled "
        "71-column supplied datasets. Worst Parent is excluded because the audit "
        "found no `TYPE` label.\n\n"
        "The model uses a simple Gaussian baseline over routing-aware features "
        "such as rank, parent count, DIO/DAO/DIS counts, hop count and packet "
        "loss. Rows are class-balanced per attack family before training. "
        "Non-numeric categorical fallback values use a deterministic BLAKE2b "
        "mapping, not Python's process-randomised hash.\n\n"
        "Important limitation: the supplied CSVs do not currently expose run IDs, "
        "so this is not yet a run-separated reproduction. Treat it as the first "
        "baseline audit result, not the final paper reproduction.\n",
        encoding="utf-8",
    )
    print(args.out_dir / "gope_baseline_results.csv")


if __name__ == "__main__":
    main()

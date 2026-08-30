#!/usr/bin/env python3
"""Evaluate the established routing-aware IDS on robustness-campaign windows."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from run_baseline_ids import metrics  # noqa: E402
from run_routing_ids import CartClassifier, GaussianClassifier, FEATURE_SETS  # noqa: E402


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["binary_label"] = row["window_label"]
    return rows


def evaluate(train: list[dict[str, str]], test: list[dict[str, str]], model_name: str, feature_set: str) -> dict[str, object]:
    model_class = CartClassifier if model_name == "cart" else GaussianClassifier
    model = model_class(FEATURE_SETS[feature_set])
    model.fit(train)
    return metrics(test, model.predict(test)) | {
        "model": model_name,
        "feature_set": feature_set,
        "train_windows": len(train),
        "test_windows": len(test),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=Path("experiments/routing_features_v1/features/routing_window_features.csv"))
    parser.add_argument("--robustness", type=Path, default=Path("experiments/robustness_campaign_v2/features/routing_window_features.csv"))
    parser.add_argument("--out", type=Path, default=Path("experiments/robustness_campaign_v2/results/ids_evaluation.csv"))
    args = parser.parse_args()

    baseline = load(args.baseline)
    robustness = load(args.robustness)
    train = [row for row in baseline if row["family"] in {"blackhole", "sinkhole"}]
    test_rows = [row for row in robustness if row["post_activation"] == "1"]
    output: list[dict[str, object]] = []
    for condition in sorted({row["condition"] for row in test_rows}):
        for family in sorted({row["family"] for row in test_rows}):
            test = [row for row in test_rows if row["condition"] == condition and row["family"] == family]
            for model_name in ("cart", "gaussian"):
                for feature_set in ("coarse", "coarse_plus_routing"):
                    output.append({"condition": condition, "family": family, **evaluate(train, test, model_name, feature_set)})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    print(f"Wrote {len(output)} robustness IDS evaluations to {args.out}")


if __name__ == "__main__":
    main()

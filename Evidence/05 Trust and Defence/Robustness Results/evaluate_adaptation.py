#!/usr/bin/env python3
"""Whole-seed adaptation under altered Cooja layout and radio conditions."""

from __future__ import annotations

import argparse
import csv
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from run_baseline_ids import metrics  # noqa: E402
from run_routing_ids import CartClassifier, FEATURE_SETS  # noqa: E402


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["binary_label"] = row["window_label"]
    return rows


def score(train: list[dict[str, str]], test: list[dict[str, str]], feature_set: str) -> dict[str, object]:
    model = CartClassifier(FEATURE_SETS[feature_set])
    model.fit(train)
    return metrics(test, model.predict(test))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=Path("experiments/routing_features_v1/features/routing_window_features.csv"))
    parser.add_argument("--robustness", type=Path, default=Path("experiments/robustness_campaign_v4/features/routing_window_features.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/robustness_campaign_v4/results"))
    args = parser.parse_args()

    baseline = [row for row in load(args.baseline) if row["family"] in {"blackhole", "sinkhole"}]
    robustness = load(args.robustness)
    detail: list[dict[str, object]] = []
    for condition in sorted({row["condition"] for row in robustness}):
        for family in sorted({row["family"] for row in robustness}):
            target = [row for row in robustness if row["condition"] == condition and row["family"] == family]
            seeds = sorted({row["seed"] for row in target})
            for feature_set in ("coarse", "coarse_plus_routing"):
                for count in range(4):
                    selections = [()] if count == 0 else combinations(seeds, count)
                    for selected in selections:
                        selected_set = set(selected)
                        adaptation = [row for row in target if row["seed"] in selected_set]
                        test = target if count == 0 else [row for row in target if row["seed"] not in selected_set]
                        detail.append({
                            "condition": condition,
                            "family": family,
                            "model": "cart",
                            "feature_set": feature_set,
                            "adaptation_seeds": count,
                            "selected_seeds": ",".join(selected),
                            "test_seeds": ",".join(seed for seed in seeds if seed not in selected_set),
                            "adaptation_windows": len(adaptation),
                            "test_windows": len(test),
                            **score(baseline + adaptation, test, feature_set),
                        })

    summary: list[dict[str, object]] = []
    keys = sorted({(r["condition"], r["family"], r["feature_set"], r["adaptation_seeds"]) for r in detail})
    for condition, family, feature_set, count in keys:
        group = [r for r in detail if (r["condition"], r["family"], r["feature_set"], r["adaptation_seeds"]) == (condition, family, feature_set, count)]
        summary.append({
            "condition": condition,
            "family": family,
            "model": "cart",
            "feature_set": feature_set,
            "adaptation_seeds": count,
            "splits": len(group),
            **{f"mean_{name}": round(sum(float(r[name]) for r in group) / len(group), 4) for name in ("accuracy", "precision", "recall", "f1", "f2", "fpr")},
        })
    write(args.out_dir / "adaptation_detail.csv", detail)
    write(args.out_dir / "adaptation_summary.csv", summary)
    print(f"Wrote {len(detail)} seed-separated evaluations and {len(summary)} summary rows")


if __name__ == "__main__":
    main()

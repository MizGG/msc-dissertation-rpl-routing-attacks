#!/usr/bin/env python3
"""Whole-seed adaptation curves for cross-attack concept drift."""

from __future__ import annotations

import argparse
import csv
import statistics
from itertools import combinations
from pathlib import Path

from run_cross_attack_drift import metrics, numeric_features, read_rows, train_model, write_csv


def mean(values: list[float]) -> float:
    return round(statistics.mean(values), 4) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", nargs="+", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/cross_attack_adaptation_v1"))
    parser.add_argument("--model", choices=("cart", "gaussian"), default="cart")
    parser.add_argument("--max-adaptation-seeds", type=int, default=3)
    parser.add_argument("--split-mode", choices=("deterministic", "all_combinations"), default="deterministic")
    parser.add_argument("--include-attack-markers", action="store_true")
    args = parser.parse_args()

    rows = read_rows(args.features)
    features = numeric_features(rows, include_attack_markers=args.include_attack_markers)
    families = sorted({row["family"] for row in rows})
    curve_rows: list[dict[str, object]] = []

    for source_family in families:
        source_rows = [row for row in rows if row["family"] == source_family]
        for target_family in families:
            if source_family == target_family:
                continue
            target_rows = [row for row in rows if row["family"] == target_family]
            target_seeds = sorted({row["seed"] for row in target_rows})
            for adaptation_seed_count in range(0, min(args.max_adaptation_seeds, len(target_seeds) - 1) + 1):
                if adaptation_seed_count == 0:
                    seed_sets = [()]
                elif args.split_mode == "all_combinations":
                    seed_sets = combinations(target_seeds, adaptation_seed_count)
                else:
                    seed_sets = [tuple(target_seeds[:adaptation_seed_count])]
                for selected in seed_sets:
                    selected_set = set(selected)
                    adaptation_rows = [row for row in target_rows if row["seed"] in selected_set]
                    evaluation_rows = [row for row in target_rows if row["seed"] not in selected_set]
                    model = train_model(args.model, features, source_rows + adaptation_rows)
                    curve_rows.append({
                        "model": args.model,
                        "source_family": source_family,
                        "target_family": target_family,
                        "adaptation_seed_count": adaptation_seed_count,
                        "adaptation_seeds": ",".join(selected),
                        "evaluation_seeds": ",".join(seed for seed in target_seeds if seed not in selected_set),
                        "features_used": len(features),
                        "source_runs": len({row["run_id"] for row in source_rows}),
                        "adaptation_runs": len({row["run_id"] for row in adaptation_rows}),
                        "evaluation_runs": len({row["run_id"] for row in evaluation_rows}),
                        "train_windows": len(source_rows) + len(adaptation_rows),
                        **metrics(evaluation_rows, model.predict(evaluation_rows)),
                    })

    summary_rows: list[dict[str, object]] = []
    for source_family in families:
        for target_family in families:
            if source_family == target_family:
                continue
            relevant = [
                row for row in curve_rows
                if row["source_family"] == source_family and row["target_family"] == target_family
            ]
            for adaptation_seed_count in range(0, args.max_adaptation_seeds + 1):
                subset = [row for row in relevant if row["adaptation_seed_count"] == adaptation_seed_count]
                if not subset:
                    continue
                summary_rows.append({
                    "model": args.model,
                    "source_family": source_family,
                    "target_family": target_family,
                    "adaptation_seed_count": adaptation_seed_count,
                    "splits": len(subset),
                    "mean_accuracy": mean([float(row["accuracy"]) for row in subset]),
                    "mean_precision": mean([float(row["precision"]) for row in subset]),
                    "mean_recall": mean([float(row["recall"]) for row in subset]),
                    "mean_f1": mean([float(row["f1"]) for row in subset]),
                    "mean_fpr": mean([float(row["fpr"]) for row in subset]),
                })

    out_dir = args.out_dir
    write_csv(out_dir / "cross_attack_adaptation_curves.csv", curve_rows)
    write_csv(out_dir / "cross_attack_adaptation_summary.csv", summary_rows)
    print(
        f"Wrote {len(curve_rows)} adaptation evaluations and "
        f"{len(summary_rows)} summary rows using {len(features)} features to {out_dir}"
    )


if __name__ == "__main__":
    main()

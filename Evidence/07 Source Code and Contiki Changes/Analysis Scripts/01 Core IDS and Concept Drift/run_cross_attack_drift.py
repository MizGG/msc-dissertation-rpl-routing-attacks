#!/usr/bin/env python3
"""Cross-attack concept-drift evaluation for Cooja routing-window features."""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from pathlib import Path

from run_routing_ids import CartClassifier, GaussianClassifier


ID_FIELDS = {
    "run_id",
    "family",
    "mode",
    "binary_run_label",
    "window_label",
    "nodes",
    "seed",
    "window_start_s",
    "window_end_s",
    "post_activation",
}


def read_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    fields: set[str] = set()
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            loaded = list(csv.DictReader(handle))
        rows.extend(loaded)
        if loaded:
            fields.update(loaded[0].keys())
    for row in rows:
        for field in fields:
            row.setdefault(field, "0")
        row["binary_label"] = row["window_label"]
    return rows


def numeric_features(rows: list[dict[str, str]], include_attack_markers: bool) -> list[str]:
    feature_names = [
        name
        for name in rows[0]
        if name not in ID_FIELDS and name != "binary_label"
    ]
    if not include_attack_markers:
        feature_names = [
            name
            for name in feature_names
            if not name.endswith("_enabled_events")
            and not name.endswith("_drop_events")
            and not name.endswith("_sent_events")
            and not name.endswith("_selection_events")
            and not name.endswith("_advertised_rank_events")
            and not name.endswith("_spoofed_dio_events")
            and name not in {"dio_suppression_events", "wormhole_endpoint_radio_events"}
        ]
    output: list[str] = []
    for name in feature_names:
        try:
            [float(row.get(name, "0") or 0) for row in rows[:5]]
        except ValueError:
            continue
        output.append(name)
    return sorted(output)


def labels(rows: list[dict[str, str]]) -> list[int]:
    return [int(row["binary_label"]) for row in rows]


def metrics(rows: list[dict[str, str]], predictions: list[int]) -> dict[str, object]:
    truth = labels(rows)
    tp = sum(1 for actual, pred in zip(truth, predictions) if actual == 1 and pred == 1)
    tn = sum(1 for actual, pred in zip(truth, predictions) if actual == 0 and pred == 0)
    fp = sum(1 for actual, pred in zip(truth, predictions) if actual == 0 and pred == 1)
    fn = sum(1 for actual, pred in zip(truth, predictions) if actual == 1 and pred == 0)
    total = len(rows)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {
        "test_windows": total,
        "accuracy": round((tp + tn) / total, 4) if total else 0.0,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def train_model(model_name: str, features: list[str], train: list[dict[str, str]]):
    model = GaussianClassifier(features) if model_name == "gaussian" else CartClassifier(features)
    model.fit(train)
    return model


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def interpretation(rows: list[dict[str, object]]) -> str:
    static = [row for row in rows if row["evaluation"] == "cross_attack"]
    cart = [row for row in static if row["model"] == "cart"]
    failures = [row for row in cart if float(row["recall"]) == 0.0]
    strong = [row for row in cart if float(row["f1"]) >= 0.8]
    lines = [
        "# Cross-Attack Concept Drift Notes",
        "",
        "This experiment treats each attack family as a separate operating environment.",
        "Models are trained on one attack/control family and tested on another family,",
        "using whole Cooja runs and 60-second windows. Labels are used only for evaluation.",
        "",
        "The main dissertation reading is not simply whether retraining works. The",
        "important question is which feature representation transfers across changed",
        "attack mechanisms and where it fails.",
        "",
        f"Total CART cross-attack pairs with zero attack recall: {len(failures)}.",
        f"Total CART cross-attack pairs with F1 >= 0.8: {len(strong)}.",
        "",
        "Zero-recall pairs are useful evidence of concept drift/model brittleness:",
    ]
    for row in failures[:20]:
        lines.append(
            f"- train {row['train_family']} -> test {row['test_family']}: "
            f"accuracy={row['accuracy']}, recall={row['recall']}, f1={row['f1']}"
        )
    if len(failures) > 20:
        lines.append(f"- plus {len(failures) - 20} more zero-recall pairs in the CSV.")
    lines.extend([
        "",
        "Methodological caution: attack-specific log marker features are excluded from",
        "the default feature set because they would leak the simulator instrumentation",
        "into the classifier. They are retained in the raw feature CSV for validation",
        "and diagnosis, not for the primary IDS claim.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", nargs="+", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/cross_attack_drift_v1"))
    parser.add_argument("--include-attack-markers", action="store_true")
    args = parser.parse_args()

    rows = read_rows(args.features)
    features = numeric_features(rows, include_attack_markers=args.include_attack_markers)
    families = sorted({row["family"] for row in rows})
    output: list[dict[str, object]] = []

    for model_name in ("gaussian", "cart"):
        for train_family in families:
            train = [row for row in rows if row["family"] == train_family]
            model = train_model(model_name, features, train)
            for test_family in families:
                test = [row for row in rows if row["family"] == test_family]
                output.append({
                    "evaluation": "in_domain" if train_family == test_family else "cross_attack",
                    "model": model_name,
                    "train_family": train_family,
                    "test_family": test_family,
                    "features_used": len(features),
                    "train_runs": len({row["run_id"] for row in train}),
                    "test_runs": len({row["run_id"] for row in test}),
                    "train_windows": len(train),
                    **metrics(test, model.predict(test)),
                })

    write_csv(args.out_dir / "cross_attack_matrix.csv", output)
    (args.out_dir / "cross_attack_interpretation.md").write_text(interpretation(output), encoding="utf-8")
    print(f"Wrote {len(output)} rows using {len(features)} features to {args.out_dir}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Evaluate local prequential IDS baselines over validated Cooja streams.

Predictions are made before each target label is revealed. A one-window delayed
label queue models supervised feedback arriving after the corresponding routing
window. The script is standard-library only and does not contact any service.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import deque
from pathlib import Path


ACTIVATION_SECONDS = 240
LABEL_DELAY_WINDOWS = 1
EPSILON = 1e-6
SENSOR_FEATURES = {
    "sinkhole": (
        "state_low_rank_nonroot_pairs",
        "state_low_rank_nonroot_senders",
        "state_receivers_exposed_low_rank_nonroot",
    ),
    "sybil": ("dio_tx_count",),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class OnlineGaussianNB:
    """Incremental Gaussian naive Bayes using Welford running statistics."""

    def __init__(self, features: list[str]) -> None:
        self.features = features
        self.counts = {0: 0, 1: 0}
        self.means = {label: [0.0] * len(features) for label in (0, 1)}
        self.m2 = {label: [0.0] * len(features) for label in (0, 1)}

    def copy(self) -> "OnlineGaussianNB":
        clone = OnlineGaussianNB(self.features)
        clone.counts = dict(self.counts)
        clone.means = {label: list(values) for label, values in self.means.items()}
        clone.m2 = {label: list(values) for label, values in self.m2.items()}
        return clone

    def reset(self) -> None:
        self.counts = {0: 0, 1: 0}
        self.means = {label: [0.0] * len(self.features) for label in (0, 1)}
        self.m2 = {label: [0.0] * len(self.features) for label in (0, 1)}

    def values(self, row: dict[str, str]) -> list[float]:
        return [float(row.get(feature, "0") or 0) for feature in self.features]

    def learn_one(self, row: dict[str, str], label: int) -> None:
        self.counts[label] += 1
        count = self.counts[label]
        for index, value in enumerate(self.values(row)):
            delta = value - self.means[label][index]
            self.means[label][index] += delta / count
            self.m2[label][index] += delta * (value - self.means[label][index])

    def learn_many(self, rows: list[dict[str, str]]) -> None:
        for row in rows:
            self.learn_one(row, int(row["window_label"]))

    def predict_one(self, row: dict[str, str]) -> int:
        total = sum(self.counts.values())
        if not total or not self.counts[0] or not self.counts[1]:
            return 0
        values = self.values(row)
        scores: dict[int, float] = {}
        for label in (0, 1):
            score = math.log(self.counts[label] / total)
            for index, value in enumerate(values):
                variance = self.m2[label][index] / max(1, self.counts[label] - 1)
                variance = max(variance, EPSILON)
                score += -0.5 * math.log(2 * math.pi * variance)
                score -= ((value - self.means[label][index]) ** 2) / (2 * variance)
            scores[label] = score
        return 1 if scores[1] > scores[0] else 0


class DDM:
    """Delayed-error Drift Detection Method with strict zero-baseline handling."""

    def __init__(self) -> None:
        self.errors: list[int] = []
        self.p_min = 1.0
        self.s_min = 0.0

    def update(self, error: int) -> str:
        self.errors.append(error)
        count = len(self.errors)
        p = sum(self.errors) / count
        s = math.sqrt(p * (1 - p) / count)
        if p + s <= self.p_min + self.s_min:
            self.p_min, self.s_min = p, s
        if p + s > self.p_min + 3 * self.s_min:
            return "drift"
        if p + s > self.p_min + 2 * self.s_min:
            return "warning"
        return "stable"


class AdaptiveErrorWindow:
    """Local adaptive error-window detector for comparison, not River ADWIN."""

    def __init__(self, min_window: int = 4, threshold: float = 0.35) -> None:
        self.errors: list[int] = []
        self.min_window = min_window
        self.threshold = threshold

    def update(self, error: int) -> str:
        self.errors.append(error)
        if len(self.errors) < self.min_window:
            return "stable"
        midpoint = len(self.errors) // 2
        older = statistics.mean(self.errors[:midpoint])
        newer = statistics.mean(self.errors[midpoint:])
        if newer - older > self.threshold:
            self.errors = self.errors[midpoint:]
            return "drift"
        return "stable"


def sensor_calibration(rows: list[dict[str, str]], features: tuple[str, ...]) -> tuple[float, float]:
    scores = [sum(float(row.get(feature, "0") or 0) for feature in features) for row in rows]
    centre = statistics.median(scores)
    mad = statistics.median(abs(score - centre) for score in scores)
    return centre, max(0.5, centre + 3 * 1.4826 * mad)


def metric_row(rows: list[dict[str, object]], name: str) -> dict[str, object]:
    truth = [int(row["window_label"]) for row in rows]
    predictions = [int(row["prediction"]) for row in rows]
    tp = sum(actual == 1 and prediction == 1 for actual, prediction in zip(truth, predictions))
    tn = sum(actual == 0 and prediction == 0 for actual, prediction in zip(truth, predictions))
    fp = sum(actual == 0 and prediction == 1 for actual, prediction in zip(truth, predictions))
    fn = sum(actual == 1 and prediction == 0 for actual, prediction in zip(truth, predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "model": name,
        "windows": len(rows),
        "accuracy": round((tp + tn) / len(rows), 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(2 * precision * recall / (precision + recall), 4) if precision + recall else 0.0,
        "fpr": round(fp / (fp + tn), 4) if fp + tn else 0.0,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def evaluate_stream(
    source: list[dict[str, str]],
    target: list[dict[str, str]],
    features: list[str],
    target_family: str,
    model_kind: str,
) -> list[dict[str, object]]:
    model = OnlineGaussianNB(features)
    model.learn_many(source)
    initial_model = model.copy()
    ddm = DDM()
    adaptive_window = AdaptiveErrorWindow()
    sensor_centre, sensor_limit = sensor_calibration(source, SENSOR_FEATURES[target_family])
    sensor_cusum = 0.0
    delayed: deque[tuple[dict[str, str], int]] = deque()
    labelled_history: list[dict[str, str]] = []
    trace: list[dict[str, object]] = []

    for row in sorted(target, key=lambda item: int(item["window_start_s"])):
        prediction = model.predict_one(row)
        sensor_score = sum(float(row.get(feature, "0") or 0) for feature in SENSOR_FEATURES[target_family])
        sensor_cusum = max(0.0, sensor_cusum + sensor_score - sensor_centre)
        sensor_alarm = int(sensor_cusum > sensor_limit)
        delayed.append((row, prediction))
        ddm_state = "awaiting_label"
        window_state = "awaiting_label"
        reset = 0
        if len(delayed) > LABEL_DELAY_WINDOWS:
            labelled_row, labelled_prediction = delayed.popleft()
            error = int(labelled_prediction != int(labelled_row["window_label"]))
            ddm_state = ddm.update(error)
            window_state = adaptive_window.update(error)
            labelled_history.append(labelled_row)
            if model_kind == "online_gaussian":
                model.learn_one(labelled_row, int(labelled_row["window_label"]))
            elif model_kind == "ddm_reset_gaussian" and ddm_state == "drift":
                model.reset()
                model.learn_many(labelled_history)
                reset = 1
            elif model_kind == "adaptive_window_reset_gaussian" and window_state == "drift":
                model.reset()
                model.learn_many(labelled_history)
                reset = 1
        trace.append({
            "model": model_kind,
            "family": row["family"],
            "mode": row["mode"],
            "seed": row["seed"],
            "window_start_s": int(row["window_start_s"]),
            "window_label": int(row["window_label"]),
            "prediction": prediction,
            "sensor_score": round(sensor_score, 4),
            "sensor_cusum": round(sensor_cusum, 4),
            "sensor_alarm": sensor_alarm,
            "ddm_state": ddm_state,
            "adaptive_window_state": window_state,
            "model_reset": reset,
            "source_model": "blackhole_gaussian_nb",
            "feature_count": len(features),
        })
        if model_kind == "static_gaussian":
            model = initial_model
    return trace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stream", type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/data/stream_windows.csv"),
    )
    parser.add_argument(
        "--manifest", type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/data/feature_manifest.json"),
    )
    parser.add_argument(
        "--out-dir", type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/results/incremental_baselines"),
    )
    args = parser.parse_args()
    rows = read_csv(args.stream)
    features = json.loads(args.manifest.read_text(encoding="utf-8"))["learning_features"]
    output: list[dict[str, object]] = []
    results: list[dict[str, object]] = []
    for family in ("sinkhole", "sybil"):
        for seed in sorted({row["seed"] for row in rows if row["family"] == family}):
            source = [row for row in rows if row["family"] == "blackhole" and row["seed"] != seed]
            for mode in ("attack", "control"):
                target = [row for row in rows if row["family"] == family and row["seed"] == seed and row["mode"] == mode]
                for model_kind in (
                    "static_gaussian",
                    "online_gaussian",
                    "ddm_reset_gaussian",
                    "adaptive_window_reset_gaussian",
                ):
                    trace = evaluate_stream(source, target, features, family, model_kind)
                    output.extend(trace)
                    summary = metric_row(trace, model_kind)
                    summary.update({"family": family, "mode": mode, "seed": seed})
                    results.append(summary)
    write_csv(args.out_dir / "prequential_window_trace.csv", output)
    write_csv(args.out_dir / "prequential_seed_results.csv", results)
    print(f"Wrote {len(output)} window rows and {len(results)} seed results to {args.out_dir}")


if __name__ == "__main__":
    main()

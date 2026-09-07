#!/usr/bin/env python3
"""Run genuine River incremental baselines with delayed-label prequential scoring.

River's ADWIN is a real adaptive-window detector. It sees delayed prediction
errors, never simulator attack markers. All execution remains local.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
from collections import deque
from pathlib import Path

from river import drift, naive_bayes, preprocessing, tree


LABEL_DELAY_WINDOWS = 1


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_model(name: str):
    classifier = (
        naive_bayes.GaussianNB()
        if name == "river_gaussian_nb"
        else tree.HoeffdingTreeClassifier(grace_period=5, delta=1e-5, leaf_prediction="nb")
    )
    return preprocessing.StandardScaler() | classifier


def values(row: dict[str, str], features: list[str]) -> dict[str, float]:
    return {feature: float(row.get(feature, "0") or 0) for feature in features}


def learn(model, rows: list[dict[str, str]], features: list[str]):
    for row in rows:
        model.learn_one(values(row, features), int(row["window_label"]))
    return model


def metrics(trace: list[dict[str, object]]) -> dict[str, object]:
    truth = [int(row["window_label"]) for row in trace]
    predictions = [int(row["prediction"]) for row in trace]
    tp = sum(actual == 1 and predicted == 1 for actual, predicted in zip(truth, predictions))
    tn = sum(actual == 0 and predicted == 0 for actual, predicted in zip(truth, predictions))
    fp = sum(actual == 0 and predicted == 1 for actual, predicted in zip(truth, predictions))
    fn = sum(actual == 1 and predicted == 0 for actual, predicted in zip(truth, predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "windows": len(trace),
        "accuracy": round((tp + tn) / len(trace), 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(2 * precision * recall / (precision + recall), 4) if precision + recall else 0.0,
        "fpr": round(fp / (fp + tn), 4) if fp + tn else 0.0,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def evaluate(initial_model, target, features, model_name, reset_on_adwin):
    model = copy.deepcopy(initial_model)
    detector = drift.ADWIN(delta=0.002)
    pending = deque()
    history = []
    trace = []
    for row in sorted(target, key=lambda item: int(item["window_start_s"])):
        prediction = int(model.predict_one(values(row, features)) or 0)
        pending.append((row, prediction))
        adwin_alarm = 0
        reset = 0
        if len(pending) > LABEL_DELAY_WINDOWS:
            labelled_row, labelled_prediction = pending.popleft()
            error = int(labelled_prediction != int(labelled_row["window_label"]))
            detector.update(error)
            adwin_alarm = int(detector.drift_detected)
            history.append(labelled_row)
            if reset_on_adwin and adwin_alarm:
                model = learn(make_model(model_name), history, features)
                reset = 1
            else:
                model.learn_one(values(labelled_row, features), int(labelled_row["window_label"]))
        trace.append({
            "model": f"{model_name}{'_adwin_reset' if reset_on_adwin else ''}",
            "family": row["family"],
            "mode": row["mode"],
            "seed": row["seed"],
            "window_start_s": int(row["window_start_s"]),
            "window_label": int(row["window_label"]),
            "prediction": prediction,
            "adwin_alarm": adwin_alarm,
            "model_reset": reset,
            "label_delay_windows": LABEL_DELAY_WINDOWS,
            "feature_count": len(features),
        })
    return trace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/data/stream_windows.csv"))
    parser.add_argument("--manifest", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/data/feature_manifest.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/results/river_incremental_baselines"))
    args = parser.parse_args()
    rows = read_csv(args.stream)
    features = json.loads(args.manifest.read_text(encoding="utf-8"))["learning_features"]
    output, summaries = [], []
    for family in ("sinkhole", "sybil"):
        for seed in sorted({row["seed"] for row in rows if row["family"] == family}):
            source = [row for row in rows if row["family"] == "blackhole" and row["seed"] != seed]
            base_models = {
                model_name: learn(make_model(model_name), source, features)
                for model_name in ("river_gaussian_nb", "river_hoeffding_tree")
            }
            for mode in ("attack", "control"):
                target = [row for row in rows if row["family"] == family and row["seed"] == seed and row["mode"] == mode]
                for model_name in ("river_gaussian_nb", "river_hoeffding_tree"):
                    for reset in (False, True):
                        trace = evaluate(base_models[model_name], target, features, model_name, reset)
                        output.extend(trace)
                        summary = metrics(trace)
                        summary.update({"model": trace[0]["model"], "family": family, "mode": mode, "seed": seed})
                        summaries.append(summary)
    write_csv(args.out_dir / "prequential_window_trace.csv", output)
    write_csv(args.out_dir / "prequential_seed_results.csv", summaries)
    print(f"Wrote {len(output)} River prequential windows and {len(summaries)} seed results to {args.out_dir}")


if __name__ == "__main__":
    main()

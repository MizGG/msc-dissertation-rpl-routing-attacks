#!/usr/bin/env python3
"""Compare label-free CUSUM and delayed-label DDM on Cooja sinkhole streams.

This is a controlled online-monitoring evaluation, not a claim that Cooja
windows arrive from a live deployment. Each sinkhole run is processed in time
order. CUSUM sees only generic rank-state telemetry. DDM sees the error of a
blackhole-trained CART prediction after a one-window label delay, mirroring the
delayed-ground-truth assumption used by supervised drift detectors.
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path

from run_routing_drift_detector import RANK_STATE_FEATURES, calibration, score
from run_routing_ids import CartClassifier, FEATURE_SETS


ACTIVATION_SECONDS = 240
LABEL_DELAY_WINDOWS = 1


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["binary_label"] = row["window_label"]
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def ddm_status(errors: list[int]) -> tuple[float, float, float, float, str]:
    """Return DDM values after the current delayed prediction error arrives."""
    p_min = 1.0
    s_min = 0.0
    status = "stable"
    for index, error in enumerate(errors, start=1):
        p = sum(errors[:index]) / index
        s = math.sqrt(p * (1.0 - p) / index)
        if p + s <= p_min + s_min:
            p_min, s_min = p, s
        # Strict comparisons avoid treating a zero-error baseline as a drift
        # alarm merely because both sides of the threshold equal zero.
        if p + s > p_min + 3 * s_min:
            status = "drift"
        elif p + s > p_min + 2 * s_min:
            status = "warning"
    return p, s, p_min, s_min, status


def monitor_run(
    rows: list[dict[str, str]],
    model: CartClassifier,
    centre: float,
    limit: float,
) -> list[dict[str, object]]:
    """Evaluate both monitors on one time-ordered attack or control run."""
    cumulative = 0.0
    delayed_errors: list[int] = []
    predictions: list[int] = []
    ordered_rows = sorted(rows, key=lambda item: int(item["window_start_s"]))
    trace: list[dict[str, object]] = []
    for index, row in enumerate(ordered_rows):
        rank_score = score(row)
        cumulative = max(0.0, cumulative + rank_score - centre)
        cusum_alarm = int(cumulative > limit)
        prediction = model.predict_one(row)
        predictions.append(prediction)
        label_available = int(index >= LABEL_DELAY_WINDOWS)
        if label_available:
            delayed_index = index - LABEL_DELAY_WINDOWS
            delayed_errors.append(int(predictions[delayed_index] != int(ordered_rows[delayed_index]["window_label"])))
            p, s, p_min, s_min, ddm_state = ddm_status(delayed_errors)
        else:
            p = s = p_min = s_min = 0.0
            ddm_state = "awaiting_label"
        trace.append({
            "run_id": row["run_id"],
            "family": row["family"],
            "mode": row["mode"],
            "seed": row["seed"],
            "window_start_s": int(row["window_start_s"]),
            "window_end_s": int(row["window_end_s"]),
            "window_label": int(row["window_label"]),
            "cart_prediction": prediction,
            "label_available": label_available,
            "cusum_rank_state_score": rank_score,
            "cusum_value": round(cumulative, 4),
            "cusum_limit": round(limit, 4),
            "cusum_alarm": cusum_alarm,
            "ddm_error_count": len(delayed_errors),
            "ddm_error_rate": round(p, 4),
            "ddm_stddev": round(s, 4),
            "ddm_error_rate_min": round(p_min, 4),
            "ddm_stddev_min": round(s_min, 4),
            "ddm_state": ddm_state,
            "ddm_alarm": int(ddm_state == "drift"),
        })
    return trace


def first_alarm(trace: list[dict[str, object]], field: str) -> int | None:
    for row in trace:
        if int(row["window_start_s"]) >= ACTIVATION_SECONDS and int(row[field]) == 1:
            return int(row["window_start_s"])
    return None


def pre_activation_alarm(trace: list[dict[str, object]], field: str) -> bool:
    return any(int(row["window_start_s"]) < ACTIVATION_SECONDS and int(row[field]) == 1 for row in trace)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--features",
        type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/routing_features_v1/features/routing_window_features.csv"),
    )
    parser.add_argument(
        "--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/online_drift_response_v1/results")
    )
    args = parser.parse_args()

    rows = read_rows(args.features)
    blackhole = [row for row in rows if row["family"] == "blackhole"]
    sinkhole = [row for row in rows if row["family"] == "sinkhole"]
    seeds = sorted({row["seed"] for row in sinkhole})
    all_trace: list[dict[str, object]] = []
    summary: list[dict[str, object]] = []

    for seed in seeds:
        # The matching source seed is excluded from both classifier training and
        # CUSUM calibration, keeping this a fully seed-separated evaluation.
        reference = [row for row in blackhole if row["seed"] != seed]
        model = CartClassifier(FEATURE_SETS["coarse_plus_routing"])
        model.fit(reference)
        centre, limit = calibration(reference)
        for mode in ("attack", "control"):
            observed = [row for row in sinkhole if row["seed"] == seed and row["mode"] == mode]
            trace = monitor_run(observed, model, centre, limit)
            all_trace.extend(trace)
            for detector, field, input_type in (
                ("rank_state_cusum", "cusum_alarm", "rank-state telemetry only"),
                ("ddm_on_delayed_cart_errors", "ddm_alarm", "delayed CART prediction errors"),
            ):
                alarm = first_alarm(trace, field)
                prealarm = pre_activation_alarm(trace, field)
                summary.append({
                    "detector": detector,
                    "mode": mode,
                    "seed": seed,
                    "reference_blackhole_seeds": ",".join(other for other in seeds if other != seed),
                    "input_type": input_type,
                    "labels_or_attack_markers_used_as_detector_inputs": "no" if detector == "rank_state_cusum" else "delayed labels only; no attack markers",
                    "pre_activation_alarm": int(prealarm),
                    "post_activation_alarm_window_s": "" if alarm is None else alarm,
                    "detection_delay_s": "" if alarm is None else alarm - ACTIVATION_SECONDS,
                    "attack_detected_without_prealarm": int(mode == "attack" and alarm is not None and not prealarm),
                    "control_false_alarm": int(mode == "control" and (alarm is not None or prealarm)),
                })

    aggregates: list[dict[str, object]] = []
    for detector in ("rank_state_cusum", "ddm_on_delayed_cart_errors"):
        attack_rows = [row for row in summary if row["detector"] == detector and row["mode"] == "attack"]
        control_rows = [row for row in summary if row["detector"] == detector and row["mode"] == "control"]
        delays = [int(row["detection_delay_s"]) for row in attack_rows if row["detection_delay_s"] != ""]
        aggregates.append({
            "detector": detector,
            "attack_runs": len(attack_rows),
            "detected_without_prealarm": sum(int(row["attack_detected_without_prealarm"]) for row in attack_rows),
            "attack_detection_rate": round(sum(int(row["attack_detected_without_prealarm"]) for row in attack_rows) / len(attack_rows), 4),
            "control_runs": len(control_rows),
            "control_false_alarms": sum(int(row["control_false_alarm"]) for row in control_rows),
            "control_false_alarm_rate": round(sum(int(row["control_false_alarm"]) for row in control_rows) / len(control_rows), 4),
            "median_detection_delay_s": statistics.median(delays) if delays else "",
            "minimum_detection_delay_s": min(delays) if delays else "",
            "maximum_detection_delay_s": max(delays) if delays else "",
        })

    write_csv(args.out_dir / "detector_window_trace.csv", all_trace)
    write_csv(args.out_dir / "detector_run_results.csv", summary)
    write_csv(args.out_dir / "detector_comparison_summary.csv", aggregates)
    print(f"Wrote online drift response evaluation to {args.out_dir}")


if __name__ == "__main__":
    main()

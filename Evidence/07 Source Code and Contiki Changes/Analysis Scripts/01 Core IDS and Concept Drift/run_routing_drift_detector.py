#!/usr/bin/env python3
"""Evaluate a seed-separated online RPL rank-state CUSUM drift monitor.

The monitor is fitted only on blackhole windows. It consumes no attack marker or
label: sinkhole labels are retained solely for the final detection evaluation.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


RANK_STATE_FEATURES = (
    "state_low_rank_nonroot_pairs",
    "state_low_rank_nonroot_senders",
    "state_receivers_exposed_low_rank_nonroot",
)
ACTIVATION_SECONDS = 240


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def score(row: dict[str, str]) -> float:
    """Aggregate persistent non-root low-rank exposure from generic RPL logs."""
    return sum(float(row[feature] or 0) for feature in RANK_STATE_FEATURES)


def calibration(rows: list[dict[str, str]]) -> tuple[float, float]:
    """Return the reference centre and a non-degenerate one-sided CUSUM limit."""
    scores = [score(row) for row in rows]
    centre = statistics.median(scores)
    deviations = [abs(value - centre) for value in scores]
    mad = statistics.median(deviations)
    # One rank-state observation is discrete. The minimum limit prevents a
    # zero-variance blackhole reference from producing a zero alarm threshold.
    limit = max(0.5, centre + 3 * 1.4826 * mad)
    return centre, limit


def monitor(rows: list[dict[str, str]], centre: float, limit: float) -> list[dict[str, object]]:
    cumulative = 0.0
    output: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: int(item["window_start_s"])):
        value = score(row)
        cumulative = max(0.0, cumulative + value - centre)
        alarm = int(cumulative > limit)
        output.append({
            "run_id": row["run_id"],
            "family": row["family"],
            "mode": row["mode"],
            "seed": row["seed"],
            "window_start_s": int(row["window_start_s"]),
            "window_end_s": int(row["window_end_s"]),
            "rank_state_score": round(value, 4),
            "reference_centre": round(centre, 4),
            "cusum": round(cumulative, 4),
            "decision_limit": round(limit, 4),
            "alarm": alarm,
            "evaluation_window_label": int(row["window_label"]),
        })
    return output


def first_alarm(rows: list[dict[str, object]], predicate) -> int | None:
    for row in rows:
        if predicate(row) and int(row["alarm"]) == 1:
            return int(row["window_start_s"])
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--features",
        type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/routing_features_v1/features/routing_window_features.csv"),
    )
    parser.add_argument(
        "--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/routing_features_v1/results")
    )
    args = parser.parse_args()

    rows = read_rows(args.features)
    blackhole = [row for row in rows if row["family"] == "blackhole"]
    sinkhole = [row for row in rows if row["family"] == "sinkhole"]
    seeds = sorted({row["seed"] for row in sinkhole})

    window_rows: list[dict[str, object]] = []
    run_rows: list[dict[str, object]] = []
    for seed in seeds:
        reference = [row for row in blackhole if row["seed"] != seed]
        centre, limit = calibration(reference)
        for mode in ("attack", "control"):
            observed = [row for row in sinkhole if row["seed"] == seed and row["mode"] == mode]
            monitored = monitor(observed, centre, limit)
            window_rows.extend(monitored)
            pre_alarm = first_alarm(monitored, lambda item: int(item["window_start_s"]) < ACTIVATION_SECONDS)
            post_alarm = first_alarm(monitored, lambda item: int(item["window_start_s"]) >= ACTIVATION_SECONDS)
            attack_detected = int(mode == "attack" and pre_alarm is None and post_alarm is not None)
            control_false_alarm = int(mode == "control" and (pre_alarm is not None or post_alarm is not None))
            run_rows.append({
                "run_id": observed[0]["run_id"],
                "mode": mode,
                "seed": seed,
                "reference_blackhole_seeds": ",".join(other for other in seeds if other != seed),
                "reference_windows": len(reference),
                "reference_centre": round(centre, 4),
                "decision_limit": round(limit, 4),
                "pre_activation_alarm_window_s": "" if pre_alarm is None else pre_alarm,
                "post_activation_alarm_window_s": "" if post_alarm is None else post_alarm,
                "detection_delay_s": "" if post_alarm is None else post_alarm - ACTIVATION_SECONDS,
                "attack_detected_without_prealarm": attack_detected,
                "control_false_alarm": control_false_alarm,
            })

    attacks = [row for row in run_rows if row["mode"] == "attack"]
    controls = [row for row in run_rows if row["mode"] == "control"]
    detected = sum(int(row["attack_detected_without_prealarm"]) for row in attacks)
    false_alarms = sum(int(row["control_false_alarm"]) for row in controls)
    delays = [int(row["detection_delay_s"]) for row in attacks if row["detection_delay_s"] != ""]
    summary = [{
        "detector": "rank_state_one_sided_cusum",
        "reference_distribution": "blackhole windows from four seeds; matching seed excluded",
        "monitored_distribution": "sinkhole attack and control windows in time order",
        "attack_runs": len(attacks),
        "attacks_detected_without_prealarm": detected,
        "attack_detection_rate": round(detected / len(attacks), 4),
        "control_runs": len(controls),
        "control_runs_with_false_alarm": false_alarms,
        "control_false_alarm_rate": round(false_alarms / len(controls), 4),
        "median_detection_delay_s": statistics.median(delays) if delays else "",
        "maximum_detection_delay_s": max(delays) if delays else "",
        "input_features": "; ".join(RANK_STATE_FEATURES),
        "labels_or_attack_markers_used_as_inputs": "no",
    }]

    write_csv(args.out_dir / "drift_detector_window_trace.csv", window_rows)
    write_csv(args.out_dir / "drift_detector_run_results.csv", run_rows)
    write_csv(args.out_dir / "drift_detector_summary.csv", summary)
    print(f"Wrote drift-detector results to {args.out_dir}")


if __name__ == "__main__":
    main()

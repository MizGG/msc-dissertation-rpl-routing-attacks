#!/usr/bin/env python3
"""Export comparable operational metrics from the sinkhole-defence campaign."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments/sinkhole_defence_v1/results/defence_condition_summary.csv"
OUTPUT = ROOT / "experiments/operational_overhead_v1/operational_overhead_table.csv"


def percentage_change(value, baseline):
    if baseline == 0:
        return "n/a"
    return round((value - baseline) * 100.0 / baseline, 2)


def main():
    with SOURCE.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    by_mode = {row["mode"]: row for row in rows}
    control = by_mode["control"]
    fieldnames = [
        "condition",
        "runs",
        "mean_application_responses",
        "application_response_change_vs_control_percent",
        "mean_missed_application_responses",
        "mean_parent_switches",
        "mean_radio_transmissions",
        "radio_transmission_change_vs_control_percent",
        "mean_defence_avoidance_log_count",
        "measurement_scope",
    ]

    labels = {
        "control": "Control",
        "attack": "Sinkhole attack",
        "defence": "Sinkhole attack with rank-parent defence",
    }
    exported = []
    for mode in ("control", "attack", "defence"):
        row = by_mode[mode]
        responses = float(row["mean_app_rx"])
        radio_tx = float(row["mean_radio_tx"])
        exported.append({
            "condition": labels[mode],
            "runs": int(row["runs"]),
            "mean_application_responses": responses,
            "application_response_change_vs_control_percent": percentage_change(
                responses, float(control["mean_app_rx"])
            ),
            "mean_missed_application_responses": float(row["mean_app_missed"]),
            "mean_parent_switches": float(row["mean_parent_switches"]),
            "mean_radio_transmissions": radio_tx,
            "radio_transmission_change_vs_control_percent": percentage_change(
                radio_tx, float(control["mean_radio_tx"])
            ),
            "mean_defence_avoidance_log_count": float(
                row["mean_defence_logged_avoidance_count"]
            ),
            "measurement_scope": "Post-activation mean across five matched Cooja seeds",
        })

    with OUTPUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(exported)


if __name__ == "__main__":
    main()

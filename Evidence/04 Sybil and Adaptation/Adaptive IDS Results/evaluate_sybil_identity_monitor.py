#!/usr/bin/env python3
"""Evaluate a transparent offline identity-consistency monitor on Cooja logs."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs_identity_observable"
SEEDS = ("123456", "234567", "345678", "456789", "567890")
WINDOW_SECONDS = 60
SIMULATION_SECONDS = 540
ACTIVATION_SECONDS = 240
IDENTITY_LINE = re.compile(r"^(\d+):(\d\d)\.\d+.*virtual identity (fd00::f[0-9a-f]{3})")


def observations_by_window(run_dir: Path) -> list[set[str]]:
    windows = [set() for _ in range(SIMULATION_SECONDS // WINDOW_SECONDS)]
    for line in (run_dir / "COOJA.testlog").read_text(encoding="utf-8", errors="replace").splitlines():
        match = IDENTITY_LINE.match(line)
        if not match:
            continue
        seconds = int(match.group(1)) * 60 + int(match.group(2))
        if 0 <= seconds < SIMULATION_SECONDS:
            windows[seconds // WINDOW_SECONDS].add(match.group(3))
    return windows


def evaluate_run(name: str, profile: str, mode: str, seed: str) -> list[dict[str, object]]:
    rows = []
    for index, identities in enumerate(observations_by_window(RUNS / name)):
        start = index * WINDOW_SECONDS
        attack_window = mode == "attack" and start >= ACTIVATION_SECONDS
        # In this controlled address plan, valid mote addresses are fd00::20x:...
        # A rotating fd00::fxxx sender is an identity-consistency violation.
        alert = bool(identities)
        rows.append({
            "run_name": name,
            "seed": seed,
            "rate_profile": profile,
            "mode": mode,
            "window_start_seconds": start,
            "virtual_identity_count": len(identities),
            "identity_consistency_alert": int(alert),
            "attack_window": int(attack_window),
        })
    return rows


def main() -> None:
    rows: list[dict[str, object]] = []
    for seed in SEEDS:
        rows.extend(evaluate_run(f"SYBIL_LOW_RATE_ATTACK_N16_SEED{seed}", "low", "attack", seed))
        rows.extend(evaluate_run(f"SYBIL_HIGH_RATE_ATTACK_N16_SEED{seed}", "high", "attack", seed))
        rows.extend(evaluate_run(f"SYBIL_LOW_RATE_CONTROL_N16_SEED{seed}", "control", "control", seed))

    output = ROOT / "results" / "sybil_identity_monitor_windows.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    attack_rows = [row for row in rows if row["attack_window"]]
    control_rows = [row for row in rows if row["mode"] == "control"]
    attack_alerts = sum(int(row["identity_consistency_alert"]) for row in attack_rows)
    control_alerts = sum(int(row["identity_consistency_alert"]) for row in control_rows)
    summary = [
        {"population": "post_activation_attack_windows", "windows": len(attack_rows), "alerts": attack_alerts, "alert_rate": attack_alerts / len(attack_rows)},
        {"population": "control_windows", "windows": len(control_rows), "alerts": control_alerts, "alert_rate": control_alerts / len(control_rows)},
    ]
    summary_path = ROOT / "results" / "sybil_identity_monitor_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary)
    print(f"Post-activation attack alerts: {attack_alerts}/{len(attack_rows)}")
    print(f"Control alerts: {control_alerts}/{len(control_rows)}")
    if attack_alerts != len(attack_rows) or control_alerts:
        raise SystemExit("Identity monitor did not meet controlled-campaign expectations")


if __name__ == "__main__":
    main()

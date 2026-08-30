#!/usr/bin/env python3
"""Summarize the isolated Sybil rate Cooja campaign from raw local logs."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SEEDS = ("123456", "234567", "345678", "456789", "567890")
ATTACK_START_SECONDS = 240.0
RADIO_LINE = re.compile(r"^\d+\t(\d+):(\d\d)\.(\d+)\t(\d+)\t.*\t(\d+)\t(\d+)$")


def time_seconds(minutes: str, seconds: str, milliseconds: str) -> float:
    return int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000


def radio_metrics(run_dir: Path) -> tuple[int, int, int, int]:
    total = post_start_total = post_start_node16 = post_start_interfered = 0
    for line in (run_dir / "COOJA.radio").read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        match = RADIO_LINE.match(line)
        if not match:
            continue
        minute, second, millisecond, sender, _bytes, interfered = match.groups()
        total += 1
        if time_seconds(minute, second, millisecond) >= ATTACK_START_SECONDS:
            post_start_total += 1
            post_start_node16 += int(sender == "16")
            post_start_interfered += int(int(interfered) > 0)
    return total, post_start_total, post_start_node16, post_start_interfered


def summarise(name: str, rate: str, mode: str, seed: str) -> dict[str, object]:
    run_dir = ROOT / "runs" / name
    log = (run_dir / "COOJA.testlog").read_text(encoding="utf-8", errors="replace")
    total, post_start_total, post_start_node16, post_start_interfered = radio_metrics(run_dir)
    marker = f"SYBIL {rate.upper()} RATE: sent spoofed multicast DIO"
    return {
        "run_name": name,
        "seed": seed,
        "rate_profile": rate,
        "mode": mode,
        "spoofed_dio_send_markers": log.count(marker) if mode == "attack" else 0,
        "radio_transmissions_total": total,
        "radio_transmissions_post_activation": post_start_total,
        "node16_transmissions_post_activation": post_start_node16,
        "interfered_transmissions_post_activation": post_start_interfered,
    }


def main() -> None:
    rows: list[dict[str, object]] = []
    for seed in SEEDS:
        rows.append(summarise(f"SYBIL_LOW_RATE_ATTACK_N16_SEED{seed}", "low", "attack", seed))
        rows.append(summarise(f"SYBIL_HIGH_RATE_ATTACK_N16_SEED{seed}", "high", "attack", seed))
        rows.append(summarise(f"SYBIL_LOW_RATE_CONTROL_N16_SEED{seed}", "control", "control", seed))

    output = ROOT / "results" / "sybil_rate_campaign_metrics.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    for rate in ("low", "high", "control"):
        group = [row for row in rows if row["rate_profile"] == rate]
        marker_mean = sum(int(row["spoofed_dio_send_markers"]) for row in group) / len(group)
        node16_mean = sum(int(row["node16_transmissions_post_activation"]) for row in group) / len(group)
        print(f"{rate}: n={len(group)}, mean_markers={marker_mean:.1f}, mean_node16_post_activation_tx={node16_mean:.1f}")

    low = [row for row in rows if row["rate_profile"] == "low"]
    high = [row for row in rows if row["rate_profile"] == "high"]
    if not all(row["spoofed_dio_send_markers"] == 29 for row in low):
        raise SystemExit("Unexpected low-rate marker count")
    if not all(row["spoofed_dio_send_markers"] == 299 for row in high):
        raise SystemExit("Unexpected high-rate marker count")


if __name__ == "__main__":
    main()

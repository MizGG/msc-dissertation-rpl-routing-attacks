#!/usr/bin/env python3
"""Extract time-window features from final Cooja attack/control runs.

The output keeps explicit attack log markers for validation, but downstream IDS
experiments should exclude those marker columns to avoid label leakage.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


RUN_DIRS = [
    Path("experiments/90 Raw Reproducibility Workspace/blackhole/final_corrected_240s_540s/runs"),
    Path("experiments/90 Raw Reproducibility Workspace/sinkhole/final_corrected_240s_540s/runs"),
]

TIME_RE = re.compile(r"^(?P<mm>\d\d):(?P<ss>\d\d)\.(?P<ms>\d{3})")
RUN_RE = re.compile(r"(?P<family>BH|SH)_(?P<mode>ATTACK|CONTROL)_N(?P<nodes>\d+)_SEED(?P<seed>\d+)")
APP_RE = re.compile(r"ID:(?P<node>\d+).*Tx/Rx/MissedTx: (?P<tx>\d+)/(?P<rx>\d+)/(?P<missed>\d+)")


def seconds_from_text(text: str) -> float | None:
    match = TIME_RE.match(text)
    if not match:
        return None
    return int(match.group("mm")) * 60 + int(match.group("ss")) + int(match.group("ms")) / 1000


def window_index(seconds: float, width: int, duration: int) -> int | None:
    if seconds < 0 or seconds >= duration:
        return None
    return int(seconds // width)


def empty_window(run_id: str, family: str, mode: str, seed: str, nodes: str, start: int, width: int) -> dict[str, int | str]:
    end = start + width
    return {
        "run_id": run_id,
        "family": family,
        "mode": mode.lower(),
        "binary_run_label": 1 if mode == "ATTACK" else 0,
        "window_label": 1 if mode == "ATTACK" and start >= 240 else 0,
        "nodes": nodes,
        "seed": seed,
        "window_start_s": start,
        "window_end_s": end,
        "post_activation": 1 if start >= 240 else 0,
        "app_tx_delta": 0,
        "app_rx_delta": 0,
        "app_missed_delta": 0,
        "app_reporting_nodes": 0,
        "parent_found_events": 0,
        "no_parent_events": 0,
        "radio_tx_count": 0,
        "radio_bytes": 0,
        "radio_interfered_count": 0,
        "unique_radio_senders": 0,
        "attacker_node16_radio_tx": 0,
        "root_node1_radio_tx": 0,
        "sinkhole_attack_enabled_events": 0,
        "sinkhole_advertised_rank_events": 0,
        "blackhole_attack_enabled_events": 0,
        "blackhole_drop_events": 0,
    }


def parse_run(run_dir: Path, width: int, duration: int) -> list[dict[str, int | str]]:
    match = RUN_RE.match(run_dir.name)
    if not match:
        raise ValueError(f"Unexpected run directory name: {run_dir}")

    family = "blackhole" if match.group("family") == "BH" else "sinkhole"
    mode = match.group("mode")
    seed = match.group("seed")
    nodes = match.group("nodes")
    windows = [
        empty_window(run_dir.name, family, mode, seed, nodes, start, width)
        for start in range(0, duration, width)
    ]
    radio_senders: list[set[str]] = [set() for _ in windows]
    app_stats: dict[str, list[tuple[float, int, int, int]]] = defaultdict(list)

    testlog = run_dir / "COOJA.testlog"
    with testlog.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            seconds = seconds_from_text(line)
            if seconds is None:
                continue
            idx = window_index(seconds, width, duration)
            if idx is None:
                continue
            row = windows[idx]
            app_match = APP_RE.search(line)
            if app_match:
                app_stats[app_match.group("node")].append((
                    seconds,
                    int(app_match.group("tx")),
                    int(app_match.group("rx")),
                    int(app_match.group("missed")),
                ))
            if "found parent:" in line:
                row["parent_found_events"] += 1
            if "no parent yet" in line:
                row["no_parent_events"] += 1
            if "SINKHOLE ATTACK: enabled" in line:
                row["sinkhole_attack_enabled_events"] += 1
            if "SINKHOLE: advertising rank" in line:
                row["sinkhole_advertised_rank_events"] += 1
            if "BLACKHOLE ATTACK: enabled" in line:
                row["blackhole_attack_enabled_events"] += 1
            if "BLACKHOLE: dropping forwarded packet" in line:
                row["blackhole_drop_events"] += 1

    for samples in app_stats.values():
        samples.sort()
        for previous, current in zip(samples, samples[1:]):
            current_idx = window_index(current[0], width, duration)
            if current_idx is None:
                continue
            windows[current_idx]["app_tx_delta"] += max(0, current[1] - previous[1])
            windows[current_idx]["app_rx_delta"] += max(0, current[2] - previous[2])
            windows[current_idx]["app_missed_delta"] += max(0, current[3] - previous[3])
            windows[current_idx]["app_reporting_nodes"] += 1

    radio = run_dir / "COOJA.radio"
    with radio.open(encoding="utf-8", errors="replace") as handle:
        next(handle, None)
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 6:
                continue
            seconds = seconds_from_text(parts[1])
            if seconds is None:
                continue
            idx = window_index(seconds, width, duration)
            if idx is None:
                continue
            sender = parts[2]
            windows[idx]["radio_tx_count"] += 1
            windows[idx]["radio_bytes"] += int(parts[4])
            windows[idx]["radio_interfered_count"] += int(parts[5])
            radio_senders[idx].add(sender)
            if sender == "16":
                windows[idx]["attacker_node16_radio_tx"] += 1
            if sender == "1":
                windows[idx]["root_node1_radio_tx"] += 1

    for idx, senders in enumerate(radio_senders):
        windows[idx]["unique_radio_senders"] = len(senders)

    return windows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=int, default=60)
    parser.add_argument("--duration", type=int, default=540)
    parser.add_argument("--out", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/features/window_features.csv"))
    args = parser.parse_args()

    rows: list[dict[str, int | str]] = []
    for base in RUN_DIRS:
        for run_dir in sorted(base.iterdir()):
            if run_dir.is_dir() and (run_dir / "COOJA.testlog").exists() and (run_dir / "COOJA.radio").exists():
                rows.extend(parse_run(run_dir, args.window, args.duration))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(args.out)


if __name__ == "__main__":
    main()

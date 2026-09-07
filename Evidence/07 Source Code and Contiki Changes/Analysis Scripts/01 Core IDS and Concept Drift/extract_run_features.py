#!/usr/bin/env python3
"""Extract run-level Cooja features from dissertation experiment logs.

The output is intentionally simple: one CSV row per simulation run. This is the
first bridge from Cooja evidence into the IDS / concept-drift pipeline.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


RUN_RE = re.compile(r"(?P<family>[A-Z]+)_(?P<mode>ATTACK|CONTROL)_N(?P<nodes>\d+)_SEED(?P<seed>\d+)")
TIME_RE = re.compile(r"^(?P<time>\d\d:\d\d\.\d{3})\t")
RADIO_RE = re.compile(r"RADIO_COUNT\t(?P<count>\d+)")
SIM_END_RE = re.compile(r"Test ended at simulation time: (?P<time_us>\d+)")


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)


def radio_transmission_count(path: Path) -> int:
    lines = count_lines(path)
    return max(lines - 1, 0) if lines else 0


def first_time(line: str) -> str:
    match = TIME_RE.search(line)
    return match.group("time") if match else ""


def parse_run(run_dir: Path) -> dict[str, str | int]:
    run_id = run_dir.name
    match = RUN_RE.fullmatch(run_id)
    if not match:
        raise ValueError(f"Unexpected run directory name: {run_id}")

    testlog = run_dir / "COOJA.testlog"
    radio = run_dir / "COOJA.radio"
    text = testlog.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    attack_enabled_lines = [line for line in lines if "ATTACK: enabled" in line]
    sinkhole_rank_lines = [line for line in lines if "SINKHOLE: advertising rank" in line]
    increase_rank_lines = [line for line in lines if "INCREASE_RANK: advertising rank" in line]
    blackhole_lines = [line for line in lines if "BLACKHOLE" in line]
    radio_counts = [int(m.group("count")) for m in map(RADIO_RE.search, lines) if m]
    sim_ends = [int(m.group("time_us")) for m in map(SIM_END_RE.search, lines) if m]

    mode = match.group("mode").lower()
    family = {
        "BH": "blackhole",
        "SH": "sinkhole",
    }.get(match.group("family"), match.group("family").lower())

    return {
        "run_id": run_id,
        "family": family,
        "mode": mode,
        "binary_label": 1 if mode == "attack" else 0,
        "nodes": int(match.group("nodes")),
        "seed": int(match.group("seed")),
        "test_ok": 1 if "TEST OK" in text else 0,
        "sim_end_us": sim_ends[-1] if sim_ends else "",
        "attack_enabled_time": first_time(attack_enabled_lines[0]) if attack_enabled_lines else "",
        "attack_enabled_events": len(attack_enabled_lines),
        "sinkhole_advertised_rank_events": len(sinkhole_rank_lines),
        "increase_rank_advertised_rank_events": len(increase_rank_lines),
        "blackhole_log_events": len(blackhole_lines),
        "app_received_requests": text.count("Received request"),
        "app_received_responses": text.count("Received response"),
        "app_not_reachable": text.count("Not reachable yet"),
        "app_tx_stat_lines": text.count("Tx/Rx/MissedTx"),
        "radio_count_reported": radio_counts[-1] if radio_counts else "",
        "radio_transmissions": radio_transmission_count(radio),
        "testlog_lines": len(lines),
        "radio_lines": count_lines(radio),
        "run_dir": str(run_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_roots", nargs="+", type=Path)
    parser.add_argument("-o", "--output", required=True, type=Path)
    args = parser.parse_args()

    rows = []
    for root in args.run_roots:
        for run_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            if (run_dir / "COOJA.testlog").exists():
                rows.append(parse_run(run_dir))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()

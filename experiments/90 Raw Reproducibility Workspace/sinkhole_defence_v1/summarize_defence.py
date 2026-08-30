#!/usr/bin/env python3
"""Summarise matched Sinkhole defence evidence without IDS-marker leakage."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REJECT_RE = re.compile(
    r"ID:(?P<node>\d+).*SINKHOLE DEFENCE: (?:rejected|avoided|retained).*\((?P<count>\d+) total\)"
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = read_rows(ROOT / "features/routing_window_features.csv")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["mode"]].append(row)

    detail: list[dict[str, object]] = []
    for mode, windows in sorted(grouped.items()):
        by_run: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in windows:
            by_run[row["run_id"]].append(row)
        for run_id, run_windows in sorted(by_run.items()):
            post = [row for row in run_windows if row["post_activation"] == "1"]
            text = (ROOT / "runs" / run_id / "COOJA.testlog").read_text(encoding="utf-8", errors="replace")
            reject_max: dict[str, int] = {}
            for match in REJECT_RE.finditer(text):
                reject_max[match.group("node")] = max(reject_max.get(match.group("node"), 0), int(match.group("count")))
            detail.append({
                "run_id": run_id,
                "mode": mode,
                "seed": run_windows[0]["seed"],
                "test_ok": int("TEST OK" in text),
                "sinkhole_rank_events": sum(int(row["sinkhole_advertised_rank_events"]) for row in post),
                "low_rank_nonroot_dio_events": sum(int(row["dio_rx_low_rank_nonroot_count"]) for row in post),
                "parent_switches": sum(int(row["parent_switch_count"]) for row in post),
                "app_rx": sum(int(row["app_rx_delta"]) for row in post),
                "app_missed": sum(int(row["app_missed_delta"]) for row in post),
                "radio_tx": sum(int(row["radio_tx_count"]) for row in post),
                "defence_logged_avoidance_count": sum(reject_max.values()),
            })

    summary: list[dict[str, object]] = []
    numeric = [key for key in detail[0] if key not in {"run_id", "mode", "seed"}]
    for mode in ("control", "attack", "defence"):
        group = [row for row in detail if row["mode"] == mode]
        summary.append({"mode": mode, "runs": len(group), **{
            f"mean_{key}": round(sum(float(row[key]) for row in group) / len(group), 2)
            for key in numeric
        }})
    write(ROOT / "results/defence_run_summary.csv", detail)
    write(ROOT / "results/defence_condition_summary.csv", summary)
    print("Wrote matched Sinkhole defence summaries for 15 runs")


if __name__ == "__main__":
    main()

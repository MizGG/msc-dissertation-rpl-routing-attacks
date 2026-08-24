#!/usr/bin/env python3
"""Validate attack activation and Cooja completion for this experiment package."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUN_RE = re.compile(r"(?P<family>DIS_FLOOD|GRAYHOLE|INCREASE_RANK|DIO_SUPPRESSION|WORST_PARENT|WORMHOLE)_(?P<mode>ATTACK|CONTROL)_N(?P<nodes>\d+)_SEED(?P<seed>\d+)")
MARKERS = {
    "DIS_FLOOD": ("DIS FLOOD ATTACK: enabled", "DIS FLOOD ATTACK: sent multicast DIS"),
    "GRAYHOLE": ("GRAYHOLE ATTACK: enabled", "GRAYHOLE: dropping forwarded packet"),
    "INCREASE_RANK": ("INCREASE RANK ATTACK: enabled", "INCREASE_RANK: advertising rank"),
    "DIO_SUPPRESSION": ("DIO SUPPRESSION ATTACK: enabled", "DIO SUPPRESSION: suppressing outgoing DIO"),
    "WORST_PARENT": ("WORST PARENT ATTACK: enabled", "WORST PARENT: selecting acceptable parent"),
    "WORMHOLE": ("WORMHOLE ATTACK: tunnel enabled between 16 and 17", ""),
}


def wormhole_endpoint_events(run_dir: Path) -> int:
    radio = run_dir / "COOJA.radio"
    if not radio.exists():
        return 0
    events = 0
    for line in radio.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        fields = line.split("\t")
        if len(fields) < 4:
            continue
        _, timestamp, source, destinations = fields[:4]
        if timestamp < "04:00.000":
            continue
        destination_set = set(destinations.split(","))
        if source == "16" and "17" in destination_set:
            events += 1
        elif source == "17" and "16" in destination_set:
            events += 1
    return events


def main() -> None:
    rows: list[dict[str, object]] = []
    for run_dir in sorted((ROOT / "runs").glob("*")):
        if not run_dir.is_dir() or RUN_RE.fullmatch(run_dir.name) is None:
            continue
        match = RUN_RE.fullmatch(run_dir.name)
        assert match is not None
        testlog = (run_dir / "COOJA.testlog").read_text(encoding="utf-8", errors="replace")
        console = (run_dir / "console.log").read_text(encoding="utf-8", errors="replace")
        activation, effect = MARKERS[match["family"]]
        is_attack = match["mode"] == "ATTACK"
        errors: list[str] = []
        if "TEST OK" not in testlog or "TEST OK" not in console:
            errors.append("missing TEST OK")
        if f"Random seed: {match['seed']}" not in testlog:
            errors.append("seed mismatch")
        if is_attack and testlog.count(activation) != 1:
            errors.append("activation missing")
        effect_events = (
            wormhole_endpoint_events(run_dir)
            if match["family"] == "WORMHOLE"
            else testlog.count(effect)
        )
        if is_attack and effect_events < 1:
            errors.append("attack effect missing")
        if not is_attack and (activation in testlog or effect_events > 0):
            errors.append("attack marker in control")
        rows.append({
            "run_id": run_dir.name,
            "family": match["family"],
            "mode": match["mode"].lower(),
            "seed": match["seed"],
            "activation_events": testlog.count(activation),
            "effect_events": effect_events,
            "status": "OK" if not errors else "FAIL: " + "; ".join(errors),
        })
    if not rows:
        raise SystemExit("No runs found")
    output = ROOT / "validation_summary.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    failures = [row["run_id"] for row in rows if row["status"] != "OK"]
    if failures:
        raise SystemExit(f"Validation failed: {', '.join(failures)}")
    print(f"Validated {len(rows)} runs")


if __name__ == "__main__":
    main()

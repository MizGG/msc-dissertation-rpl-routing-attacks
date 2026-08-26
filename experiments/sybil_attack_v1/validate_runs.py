#!/usr/bin/env python3
"""Validate Sybil attack activation and spoofed RPL identity evidence."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUN_RE = re.compile(r"SYBIL_(?P<mode>ATTACK|CONTROL)_N16_SEED(?P<seed>\d+)")
ACTIVATION = "SYBIL ATTACK: enabled"
EFFECT = "SYBIL: sending RPL DIO as virtual identity"


def main() -> None:
    rows: list[dict[str, object]] = []
    for run_dir in sorted((ROOT / "runs").glob("*")):
        match = RUN_RE.fullmatch(run_dir.name)
        if not run_dir.is_dir() or match is None:
            continue
        testlog = (run_dir / "COOJA.testlog").read_text(encoding="utf-8", errors="replace")
        console = (run_dir / "console.log").read_text(encoding="utf-8", errors="replace")
        is_attack = match["mode"] == "ATTACK"
        activation_events = testlog.count(ACTIVATION)
        effect_events = testlog.count(EFFECT)
        errors: list[str] = []
        if "TEST OK" not in testlog or "TEST OK" not in console:
            errors.append("missing TEST OK")
        if f"Random seed: {match['seed']}" not in testlog:
            errors.append("seed mismatch")
        if is_attack and activation_events != 1:
            errors.append("activation missing")
        if is_attack and effect_events < 1:
            errors.append("spoofed DIO missing")
        if not is_attack and (activation_events > 0 or effect_events > 0):
            errors.append("Sybil marker in control")
        rows.append({
            "run_id": run_dir.name,
            "family": "sybil",
            "mode": match["mode"].lower(),
            "seed": match["seed"],
            "activation_events": activation_events,
            "effect_events": effect_events,
            "status": "OK" if not errors else "FAIL: " + "; ".join(errors),
        })
    if not rows:
        raise SystemExit("No Sybil runs found")
    output = ROOT / "validation_summary.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    failures = [row["run_id"] for row in rows if row["status"] != "OK"]
    if failures:
        raise SystemExit(f"Validation failed: {', '.join(failures)}")
    print(f"Validated {len(rows)} Sybil runs")


if __name__ == "__main__":
    main()

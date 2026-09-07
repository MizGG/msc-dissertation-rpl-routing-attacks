#!/usr/bin/env python3
"""Validate completion and expected attack/control markers for Sybil rate runs."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SEEDS = ("123456", "234567", "345678", "456789", "567890")


def inspect(name: str, expected_prefix: str | None) -> dict[str, object]:
    run = ROOT / "runs" / name
    text = (run / "COOJA.testlog").read_text(encoding="utf-8", errors="replace") if (run / "COOJA.testlog").is_file() else ""
    console = (run / "console.log").read_text(encoding="utf-8", errors="replace") if (run / "console.log").is_file() else ""
    sent = text.count(f"{expected_prefix}: sent spoofed multicast DIO") if expected_prefix else 0
    return {
        "run_name": name,
        "mode": "attack" if expected_prefix else "control",
        "test_ok": int("TEST OK" in text or "TEST OK" in console),
        "radio_present": int((run / "COOJA.radio").is_file()),
        "startup_markers": text.count(f"{expected_prefix}: started, attack disabled") if expected_prefix else text.count("SYBIL RATE CONTROL: started, normal RPL behaviour"),
        "enable_markers": text.count(f"{expected_prefix}: enabled") if expected_prefix else 0,
        "spoofed_dio_send_markers": sent,
        "valid": 0,
    }


def main() -> None:
    rows = []
    for seed in SEEDS:
        rows.append(inspect(f"SYBIL_LOW_RATE_ATTACK_N16_SEED{seed}", "SYBIL LOW RATE"))
        rows.append(inspect(f"SYBIL_HIGH_RATE_ATTACK_N16_SEED{seed}", "SYBIL HIGH RATE"))
        rows.append(inspect(f"SYBIL_LOW_RATE_CONTROL_N16_SEED{seed}", None))
    for row in rows:
        attack = row["mode"] == "attack"
        row["valid"] = int(
            row["test_ok"] and row["radio_present"] and row["startup_markers"] == 1
            and ((row["enable_markers"] == 1 and row["spoofed_dio_send_markers"] > 0) if attack else row["enable_markers"] == 0)
        )
    out = ROOT / "results" / "sybil_rate_campaign_validation.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    invalid = [row["run_name"] for row in rows if not row["valid"]]
    print(f"Validated {len(rows) - len(invalid)}/{len(rows)} Sybil rate configurations")
    if invalid:
        raise SystemExit("Invalid configurations: " + ", ".join(invalid))


if __name__ == "__main__":
    main()

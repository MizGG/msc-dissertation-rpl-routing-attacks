#!/usr/bin/env python3
"""Validate Cooja completion and attack markers for the robustness campaign."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SEEDS = ("123456", "234567", "345678", "456789", "567890")
CONDITIONS = ("ATTACKER_RELOCATED", "LOSSY_RADIO")
FAMILIES = {
    "BH": ("BLACKHOLE", "BLACKHOLE: dropping forwarded packet"),
    "SH": ("SINKHOLE", "SINKHOLE: advertising rank"),
    "SYBIL": ("SYBIL", "SYBIL ATTACK: sent spoofed multicast DIO"),
}


def inspect(name: str, family: str, mode: str) -> dict[str, object]:
    run = ROOT / "runs" / name
    text = (run / "COOJA.testlog").read_text(encoding="utf-8", errors="replace") if (run / "COOJA.testlog").is_file() else ""
    _, attack_marker = FAMILIES[family]
    marker_count = text.count(attack_marker)
    return {
        "run_name": name,
        "family": family,
        "mode": mode.lower(),
        "test_ok": int("TEST OK" in text),
        "radio_present": int((run / "COOJA.radio").is_file()),
        "attack_marker_count": marker_count,
        "valid": 0,
    }


def main() -> None:
    rows: list[dict[str, object]] = []
    for condition in CONDITIONS:
        for family in FAMILIES:
            for mode in ("ATTACK", "CONTROL"):
                for seed in SEEDS:
                    name = f"{condition}_{family}_{mode}_N16_SEED{seed}"
                    row = inspect(name, family, mode)
                    row["valid"] = int(row["test_ok"] and row["radio_present"] and ((row["attack_marker_count"] > 0) if mode == "ATTACK" else row["attack_marker_count"] == 0))
                    rows.append(row)
    out = ROOT / "results" / "campaign_validation.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    invalid = [str(row["run_name"]) for row in rows if not row["valid"]]
    print(f"Validated {len(rows) - len(invalid)}/{len(rows)} robustness configurations")
    if invalid:
        raise SystemExit("Invalid configurations: " + ", ".join(invalid))


if __name__ == "__main__":
    main()

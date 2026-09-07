#!/usr/bin/env python3
"""Validate observable Sybil identity churn in separately stored Cooja logs."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs_identity_observable"
SEEDS = ("123456", "234567", "345678", "456789", "567890")
IDENTITY = re.compile(r"virtual identity (fd00::f[0-9a-f]{3})")


def inspect(name: str, profile: str, mode: str, seed: str) -> dict[str, object]:
    run = RUNS / name
    log = (run / "COOJA.testlog").read_text(encoding="utf-8", errors="replace")
    identities = IDENTITY.findall(log)
    marker = f"SYBIL {profile.upper()} RATE: sent spoofed multicast DIO"
    sends = log.count(marker) if mode == "attack" else 0
    return {
        "run_name": name,
        "seed": seed,
        "rate_profile": profile,
        "mode": mode,
        "test_ok": int("TEST OK" in log),
        "spoofed_dio_sends": sends,
        "virtual_identity_observations": len(identities),
        "distinct_virtual_identities": len(set(identities)),
        "identity_churn_events": max(0, len(identities) - 1),
        "valid": 0,
    }


def main() -> None:
    rows: list[dict[str, object]] = []
    for seed in SEEDS:
        rows.append(inspect(f"SYBIL_LOW_RATE_ATTACK_N16_SEED{seed}", "low", "attack", seed))
        rows.append(inspect(f"SYBIL_HIGH_RATE_ATTACK_N16_SEED{seed}", "high", "attack", seed))
        rows.append(inspect(f"SYBIL_LOW_RATE_CONTROL_N16_SEED{seed}", "control", "control", seed))

    for row in rows:
        if row["mode"] == "attack":
            row["valid"] = int(
                row["test_ok"]
                and row["spoofed_dio_sends"] > 0
                # Natural RPL DIOs emitted after activation also traverse the
                # existing hook, so the observable identity count can exceed
                # the application's scheduled spoofed-DIO count.
                and row["virtual_identity_observations"] >= row["spoofed_dio_sends"]
                and row["distinct_virtual_identities"] == 16
            )
        else:
            row["valid"] = int(row["test_ok"] and row["virtual_identity_observations"] == 0)

    output = ROOT / "results" / "sybil_identity_consistency.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    invalid = [str(row["run_name"]) for row in rows if not row["valid"]]
    print(f"Validated {len(rows) - len(invalid)}/{len(rows)} identity-observable configurations")
    if invalid:
        raise SystemExit("Invalid configurations: " + ", ".join(invalid))


if __name__ == "__main__":
    main()

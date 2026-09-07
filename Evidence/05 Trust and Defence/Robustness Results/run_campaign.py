#!/usr/bin/env python3
"""Run or resume the isolated Cooja robustness campaign sequentially."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNNER = ROOT.parent / "adversarial_rl_sybil_v1" / "run_cooja_config.py"
SEEDS = ("123456", "234567", "345678", "456789", "567890")
CONDITIONS = ("ATTACKER_RELOCATED", "LOSSY_RADIO")
FAMILIES = ("BH", "SH", "SYBIL")


def run(name: str) -> None:
    run_dir = ROOT / "runs" / name
    if (run_dir / "COOJA.testlog").is_file() and (run_dir / "COOJA.radio").is_file():
        print(f"Skipping completed run: {name}")
        return
    config = ROOT / "configs" / f"{name}.csc"
    subprocess.run([sys.executable, str(RUNNER), str(config), "--run-dir", str(run_dir)], check=True)


def main() -> None:
    names = [
        f"{condition}_{family}_{mode}_N16_SEED{seed}"
        for condition in CONDITIONS
        for family in FAMILIES
        for mode in ("ATTACK", "CONTROL")
        for seed in SEEDS
    ]
    for name in names:
        run(name)
    print(f"Completed or verified {len(names)} robustness configurations")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run or resume the three-condition Sinkhole defence campaign."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNNER = ROOT.parent / "adversarial_rl_sybil_v1" / "run_cooja_config.py"
SEEDS = ("123456", "234567", "345678", "456789", "567890")


def main() -> None:
    for mode in ("CONTROL", "ATTACK", "DEFENCE"):
        for seed in SEEDS:
            name = f"SH_{mode}_N16_SEED{seed}"
            run_dir = ROOT / "runs" / name
            if (run_dir / "COOJA.testlog").is_file() and (run_dir / "COOJA.radio").is_file():
                print(f"Skipping completed run: {name}")
                continue
            subprocess.run([sys.executable, str(RUNNER), str(ROOT / "configs" / f"{name}.csc"), "--run-dir", str(run_dir)], check=True)
    print("Completed or verified 15 Sinkhole defence configurations")


if __name__ == "__main__":
    main()

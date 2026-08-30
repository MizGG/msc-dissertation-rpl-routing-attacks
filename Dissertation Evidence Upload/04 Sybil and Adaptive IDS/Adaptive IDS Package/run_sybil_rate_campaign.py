#!/usr/bin/env python3
"""Execute the isolated five-seed Sybil DIO-rate Cooja campaign sequentially."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNNER = ROOT / "run_cooja_config.py"
SEEDS = ("123456", "234567", "345678", "456789", "567890")


def run(config_name: str, runs_dir: Path) -> None:
    config = ROOT / "configs" / f"{config_name}.csc"
    run_dir = runs_dir / config_name
    if (run_dir / "COOJA.testlog").is_file() and (run_dir / "COOJA.radio").is_file():
        print(f"Skipping completed run: {config_name}")
        return
    command = [sys.executable, str(RUNNER), str(config), "--run-dir", str(run_dir)]
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=ROOT / "runs",
        help="isolated output directory; defaults to the validated rate campaign",
    )
    args = parser.parse_args()
    requested = []
    for seed in SEEDS:
        requested.append(f"SYBIL_LOW_RATE_ATTACK_N16_SEED{seed}")
        requested.append(f"SYBIL_HIGH_RATE_ATTACK_N16_SEED{seed}")
        requested.append(f"SYBIL_LOW_RATE_CONTROL_N16_SEED{seed}")
    for config_name in requested:
        run(config_name, args.runs_dir)
    print(f"Completed or verified {len(requested)} isolated Sybil rate campaign configurations")


if __name__ == "__main__":
    main()

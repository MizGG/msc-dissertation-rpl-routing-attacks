#!/usr/bin/env python3
"""Run one isolated Cooja configuration headlessly and preserve its raw logs."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
COOJA_DIR = Path("/Users/mizzy/contiki-ng/tools/cooja")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path, help="Cooja .csc configuration")
    parser.add_argument("--run-dir", type=Path, required=True, help="new isolated Cooja log directory")
    args = parser.parse_args()
    config = args.config.resolve()
    if not config.is_file() or config.suffix != ".csc":
        raise SystemExit(f"Cooja configuration not found: {config}")
    if not COOJA_DIR.is_dir():
        raise SystemExit(f"Cooja installation not found: {COOJA_DIR}")
    args.run_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "./gradlew",
        "run",
        f"--args=--no-gui --logdir {args.run_dir.resolve()} {config}",
    ]
    completed = subprocess.run(
        command,
        cwd=COOJA_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (args.run_dir / "console.log").write_text(completed.stdout, encoding="utf-8")
    if completed.returncode:
        raise SystemExit(completed.returncode)
    print(f"Cooja completed: {config.name} -> {args.run_dir}")


if __name__ == "__main__":
    main()

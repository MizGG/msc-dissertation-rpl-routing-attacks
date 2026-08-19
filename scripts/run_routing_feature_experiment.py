#!/usr/bin/env python3
"""Run the isolated routing-aware Cooja experiment sequentially."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


COOJA_DIR = Path("/Users/mizzy/contiki-ng/tools/cooja")


def is_complete(run_dir: Path) -> bool:
    testlog = run_dir / "COOJA.testlog"
    radio = run_dir / "COOJA.radio"
    return testlog.is_file() and radio.is_file() and "TEST OK" in testlog.read_text(
        encoding="utf-8", errors="replace"
    )


def run_config(config: Path, runs_dir: Path, timeout_seconds: int) -> None:
    run_dir = runs_dir / config.stem
    if is_complete(run_dir):
        print(f"SKIP {config.stem}: complete")
        return
    if run_dir.exists():
        partial_files = {path.name for path in run_dir.iterdir()}
        if partial_files - {"console.log"}:
            raise RuntimeError(f"Partial run exists; inspect before retrying: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "./gradlew",
        "run",
        f"--args=--no-gui --logdir {run_dir.resolve()} {config.resolve()}",
    ]
    print(f"RUN  {config.stem}")
    with (run_dir / "console.log").open("w", encoding="utf-8") as console:
        completed = subprocess.run(
            command,
            cwd=COOJA_DIR,
            stdout=console,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    if completed.returncode != 0 or not is_complete(run_dir):
        raise RuntimeError(f"Cooja run failed: {config.stem}; see {run_dir / 'console.log'}")
    print(f"OK   {config.stem}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-dir", type=Path, default=Path("experiments/routing_features_v1"))
    parser.add_argument("--match", default="*.csc")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    configs = sorted((args.experiment_dir / "configs").glob(args.match))
    if args.limit is not None:
        configs = configs[: args.limit]
    if not configs:
        raise SystemExit("No matching Cooja configs")
    for config in configs:
        run_config(config, args.experiment_dir / "runs", args.timeout_seconds)
    print(f"Completed {len(configs)} requested runs")


if __name__ == "__main__":
    main()

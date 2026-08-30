#!/usr/bin/env python3
"""Validate routing-feature Cooja runs and write an auditable evidence summary."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


TIME_RE = re.compile(r"^(?P<mm>\d+):(?P<ss>\d\d)\.(?P<ms>\d{3})")
RUN_RE = re.compile(r"(?P<family>BH|SH)_(?P<mode>ATTACK|CONTROL)_N(?P<nodes>\d+)_SEED(?P<seed>\d+)")
NODE16_DIO_RE = re.compile(r"received a .*DIO from fe80::210:10:10:10,.* rank (?P<rank>\d+)$")


def seconds_from_line(line: str) -> float | None:
    match = TIME_RE.match(line)
    if match is None:
        return None
    return int(match.group("mm")) * 60 + int(match.group("ss")) + int(match.group("ms")) / 1000


def validate_run(run_dir: Path, corrected: bool) -> dict[str, object]:
    match = RUN_RE.fullmatch(run_dir.name)
    if match is None:
        raise ValueError(f"Unexpected run name: {run_dir.name}")
    text = (run_dir / "COOJA.testlog").read_text(encoding="utf-8", errors="replace")
    console = (run_dir / "console.log").read_text(encoding="utf-8", errors="replace")
    post_ranks: list[int] = []
    for line in text.splitlines():
        seconds = seconds_from_line(line)
        dio = NODE16_DIO_RE.search(line)
        if seconds is not None and seconds >= 240 and dio:
            post_ranks.append(int(dio.group("rank")))

    family = "blackhole" if match.group("family") == "BH" else "sinkhole"
    mode = match.group("mode").lower()
    sinkhole_enabled = text.count("SINKHOLE ATTACK: enabled")
    sinkhole_hook = text.count("SINKHOLE: advertising rank")
    blackhole_enabled = text.count("BLACKHOLE ATTACK: enabled")
    blackhole_drops = text.count("BLACKHOLE: dropping forwarded packet")
    errors: list[str] = []
    if "TEST OK" not in text or "TEST OK" not in console:
        errors.append("missing TEST OK")
    if f"Random seed: {match.group('seed')}" not in text:
        errors.append("seed mismatch")
    if family == "sinkhole" and mode == "attack":
        if sinkhole_enabled != 1 or sinkhole_hook < 1:
            errors.append("sinkhole activation missing")
        if not post_ranks:
            errors.append("no post-activation node16 DIO")
        if corrected and set(post_ranks) != {128}:
            errors.append(f"non-persistent sinkhole ranks {sorted(set(post_ranks))}")
    if family == "sinkhole" and mode == "control":
        if sinkhole_enabled or sinkhole_hook:
            errors.append("sinkhole marker in control")
        if 128 in post_ranks:
            errors.append("low non-root rank in control")
    if family == "blackhole" and mode == "attack":
        if blackhole_enabled != 1 or blackhole_drops < 1:
            errors.append("blackhole activation/drop missing")
    if family == "blackhole" and mode == "control" and (blackhole_enabled or blackhole_drops):
        errors.append("blackhole marker in control")

    return {
        "run_id": run_dir.name,
        "family": family,
        "mode": mode,
        "seed": match.group("seed"),
        "test_ok": 1 if "TEST OK" in text and "TEST OK" in console else 0,
        "sinkhole_enabled_events": sinkhole_enabled,
        "sinkhole_hook_events": sinkhole_hook,
        "blackhole_enabled_events": blackhole_enabled,
        "blackhole_drop_events": blackhole_drops,
        "post_activation_node16_dio_rx": len(post_ranks),
        "post_activation_node16_ranks": ";".join(str(value) for value in sorted(set(post_ranks))),
        "status": "OK" if not errors else "FAIL: " + "; ".join(errors),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_checksums(base: Path) -> None:
    checksum_path = base / "SHA256SUMS.txt"
    lines: list[str] = []
    for path in sorted(item for item in base.rglob("*") if item.is_file()):
        if path == checksum_path or "build" in path.parts:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(base)}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/routing_features_v1"))
    parser.add_argument(
        "--diagnostic-dir",
        type=Path,
        default=Path("experiments/90 Raw Reproducibility Workspace/routing_features_weak_flag_diagnostic"),
    )
    args = parser.parse_args()

    run_dirs = sorted(path for path in (args.experiment_dir / "runs").iterdir() if path.is_dir())
    if len(run_dirs) != 20:
        raise ValueError(f"Expected 20 corrected runs; found {len(run_dirs)}")
    corrected_rows = [validate_run(path, corrected=True) for path in run_dirs]
    write_csv(args.experiment_dir / "validation_summary.csv", corrected_rows)
    failures = [row for row in corrected_rows if row["status"] != "OK"]
    if failures:
        raise ValueError(f"Corrected validation failures: {[row['run_id'] for row in failures]}")

    diagnostic_runs = sorted(path for path in (args.diagnostic_dir / "runs").iterdir() if path.is_dir())
    diagnostic_rows = [validate_run(path, corrected=False) for path in diagnostic_runs]
    write_csv(args.diagnostic_dir / "validation_summary.csv", diagnostic_rows)
    write_checksums(args.experiment_dir)
    print(f"Validated {len(corrected_rows)} corrected runs and {len(diagnostic_rows)} diagnostic runs")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the frozen baseline Cooja dataset from validated feature extracts."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ROOT / "experiments/cross_attack_drift_v1/features/bh_sh_routing_window_features.csv",
    ROOT / "experiments/cross_attack_drift_v1/features/additional_routing_window_features.csv",
    ROOT / "experiments/sybil_attack_v1/features/routing_window_features.csv",
]
OUT_DIR = ROOT / "experiments/final_simulated_dataset_v1/data"
DATASET = OUT_DIR / "cooja_rpl_baseline_windows_v1.csv"
MANIFEST = OUT_DIR / "cooja_rpl_baseline_run_manifest_v1.csv"
VALIDATION = OUT_DIR / "validation_summary.txt"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def main() -> None:
    canonical_fields, _ = read_csv(SOURCES[0])
    output_fields = ["source_feature_file"] + canonical_fields
    rows: list[dict[str, str]] = []

    for source in SOURCES:
        fields, source_rows = read_csv(source)
        missing = [field for field in canonical_fields if field not in fields]
        if missing:
            raise ValueError(f"{source} does not contain canonical fields: {missing}")
        for row in source_rows:
            canonical_row = {field: row[field] for field in canonical_fields}
            canonical_row["source_feature_file"] = str(source.relative_to(ROOT))
            rows.append(canonical_row)

    family_counts = Counter(row["family"] for row in rows)
    expected_families = {
        "blackhole", "sinkhole", "dis_flood", "grayhole", "increase_rank",
        "dio_suppression", "worst_parent", "wormhole", "sybil",
    }
    if set(family_counts) != expected_families:
        raise ValueError(f"Unexpected family coverage: {dict(family_counts)}")
    if any(count != 90 for count in family_counts.values()):
        raise ValueError(f"Expected 90 windows per family: {dict(family_counts)}")

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["family"], row["mode"], row["seed"])].append(row)
    if len(grouped) != 90:
        raise ValueError(f"Expected 90 family/mode/seed groups, found {len(grouped)}")
    if any(len(group) != 9 for group in grouped.values()):
        raise ValueError("Every complete run must contain nine 60-second windows")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with DATASET.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    manifest_rows = []
    for (family, mode, seed), windows in sorted(grouped.items()):
        starts = sorted(int(row["window_start_s"]) for row in windows)
        manifest_rows.append({
            "group_id": f"{family}:{mode}:{seed}",
            "family": family,
            "mode": mode,
            "seed": seed,
            "run_id": windows[0]["run_id"],
            "source_feature_file": windows[0]["source_feature_file"],
            "window_count": len(windows),
            "window_starts_s": ";".join(map(str, starts)),
            "attack_activation_s": 240,
        })
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest_rows)

    summary = [
        "Frozen Cooja RPL baseline dataset v1",
        f"rows={len(rows)}",
        f"run_groups={len(grouped)}",
        "families=" + ",".join(sorted(family_counts)),
        "windows_per_group=9",
        "window_width_seconds=60",
        "attack_activation_seconds=240",
        "validation=PASS",
    ]
    VALIDATION.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} windows and {len(manifest_rows)} run groups to {OUT_DIR}")


if __name__ == "__main__":
    main()

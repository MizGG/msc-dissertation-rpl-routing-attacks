#!/usr/bin/env python3
"""Build an ordered local stream from validated Cooja routing-window features.

The resulting dataset is an isolated copy for the adaptive IDS extension.
Existing experiment inputs are read only. Simulator attack markers remain in
the raw output for validation, but the feature manifest excludes them from every
learning or controller stage.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_INPUTS = (
    Path("experiments/90 Raw Reproducibility Workspace/routing_features_v1/features/routing_window_features.csv"),
    Path("experiments/90 Raw Reproducibility Workspace/sybil_attack_v1/features/routing_window_features.csv"),
)
DEFAULT_OUTPUT = Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/data")

METADATA_FIELDS = {
    "run_id",
    "family",
    "mode",
    "binary_run_label",
    "window_label",
    "nodes",
    "seed",
    "window_start_s",
    "window_end_s",
    "post_activation",
    "stream_id",
    "stream_sequence",
}
MARKER_NAMES = {
    "dio_suppression_events",
    "wormhole_endpoint_radio_events",
}
MARKER_SUFFIXES = (
    "_enabled_events",
    "_drop_events",
    "_sent_events",
    "_selection_events",
    "_advertised_rank_events",
    "_spoofed_dio_events",
)
ATTACK_IMPLEMENTATION_PREFIXES = (
    "blackhole_",
    "sinkhole_",
    "sybil_",
    "grayhole_",
    "dis_flood_",
    "increase_rank_",
    "dio_suppression_",
    "worst_parent_",
    "wormhole_",
)


def is_marker(field: str) -> bool:
    return (
        field in MARKER_NAMES
        or field.endswith(MARKER_SUFFIXES)
        or field.startswith(ATTACK_IMPLEMENTATION_PREFIXES)
    )


def load_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, reader.fieldnames or []


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", type=Path, default=list(DEFAULT_INPUTS))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    by_key: dict[tuple[str, str, str, int], dict[str, str]] = {}
    fields: set[str] = set()
    source_rows: dict[str, int] = {}
    for path in args.inputs:
        rows, current_fields = load_csv(path)
        source_rows[str(path)] = len(rows)
        fields.update(current_fields)
        for row in rows:
            if row.get("family") not in {"blackhole", "sinkhole", "sybil"}:
                continue
            key = (
                row["family"],
                row["mode"],
                row["seed"],
                int(row["window_start_s"]),
            )
            if key in by_key:
                raise ValueError(f"duplicate stream window: {key}")
            by_key[key] = row

    output_fields = sorted(fields | {"stream_id", "stream_sequence"})
    rows: list[dict[str, str]] = []
    for sequence, (_, row) in enumerate(sorted(by_key.items()), start=1):
        normalised = {field: row.get(field, "0") for field in output_fields}
        normalised["stream_id"] = f"{row['family']}:{row['mode']}:{row['seed']}"
        normalised["stream_sequence"] = str(sequence)
        rows.append(normalised)

    feature_fields = [
        field for field in output_fields
        if field not in METADATA_FIELDS and not is_marker(field)
    ]
    marker_fields = sorted(field for field in output_fields if is_marker(field))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "stream_windows.csv", output_fields, rows)
    (args.out_dir / "feature_manifest.json").write_text(
        json.dumps(
            {
                "families": ["blackhole", "sinkhole", "sybil"],
                "source_files": source_rows,
                "stream_windows": len(rows),
                "streams": len({row["stream_id"] for row in rows}),
                "learning_features": feature_fields,
                "excluded_attack_marker_fields": marker_fields,
                "metadata_fields": sorted(METADATA_FIELDS),
                "policy": "attack markers are validation-only and excluded from all learning stages",
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(rows)} windows from {len(source_rows)} inputs to {args.out_dir}")


if __name__ == "__main__":
    main()

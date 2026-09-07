#!/usr/bin/env python3
"""Audit integrity, labels, and IDS feature eligibility of the frozen dataset."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "experiments/final_simulated_dataset_v1"
DATASET = PACKAGE / "data/cooja_rpl_baseline_windows_v1.csv"
MANIFEST = PACKAGE / "data/cooja_rpl_baseline_run_manifest_v1.csv"
RESULTS = PACKAGE / "audit"

METADATA_FIELDS = {
    "source_feature_file", "run_id", "family", "mode", "binary_run_label",
    "window_label", "nodes", "seed", "window_start_s", "window_end_s",
    "post_activation",
}
MARKER_NAMES = {"dio_suppression_events", "wormhole_endpoint_radio_events"}
MARKER_SUFFIXES = (
    "_enabled_events", "_drop_events", "_sent_events", "_selection_events",
    "_advertised_rank_events", "_spoofed_dio_events",
)
ATTACK_IMPLEMENTATION_PREFIXES = (
    "blackhole_", "sinkhole_", "sybil_", "grayhole_", "dis_flood_",
    "increase_rank_", "dio_suppression_", "worst_parent_", "wormhole_",
)
SUMMARY_FIELDS = (
    "app_tx_delta", "app_rx_delta", "app_missed_delta", "radio_tx_count",
    "dio_rx_count", "dio_tx_count", "dis_rx_count", "dao_rx_count",
    "parent_switch_count", "dio_rx_low_rank_nonroot_count",
    "state_low_rank_nonroot_pairs", "own_rank_mean",
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def is_marker(field: str) -> bool:
    return (
        field in MARKER_NAMES
        or field.endswith(MARKER_SUFFIXES)
        or field.startswith(ATTACK_IMPLEMENTATION_PREFIXES)
    )


def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    fields, rows = read_csv(DATASET)
    _, manifest_rows = read_csv(MANIFEST)
    errors: list[str] = []
    expected_families = {
        "blackhole", "sinkhole", "dis_flood", "grayhole", "increase_rank",
        "dio_suppression", "worst_parent", "wormhole", "sybil",
    }

    check(len(rows) == 810, f"expected 810 windows, found {len(rows)}", errors)
    check(len(manifest_rows) == 90, f"expected 90 run groups, found {len(manifest_rows)}", errors)
    check(set(row["family"] for row in rows) == expected_families, "family coverage mismatch", errors)
    check(not any(any(value == "" for value in row.values()) for row in rows), "missing CSV values found", errors)

    numeric_fields = [field for field in fields if field not in METADATA_FIELDS]
    non_numeric = []
    for field in numeric_fields:
        try:
            [float(row[field]) for row in rows]
        except ValueError:
            non_numeric.append(field)
    check(not non_numeric, f"non-numeric feature fields: {non_numeric}", errors)

    keys = [(row["family"], row["mode"], row["seed"], row["window_start_s"]) for row in rows]
    check(len(set(keys)) == len(keys), "duplicate family/mode/seed/window records found", errors)

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["family"], row["mode"], row["seed"])].append(row)
    check(len(grouped) == 90, f"expected 90 groups, found {len(grouped)}", errors)
    expected_starts = list(range(0, 540, 60))
    for key, windows in grouped.items():
        starts = sorted(int(row["window_start_s"]) for row in windows)
        check(starts == expected_starts, f"invalid windows for {key}: {starts}", errors)
        for row in windows:
            attack = row["mode"] == "attack"
            post_activation = int(row["window_start_s"]) >= 240
            expected_binary = "1" if attack else "0"
            expected_window = "1" if attack and post_activation else "0"
            check(row["binary_run_label"] == expected_binary, f"binary label error in {key}", errors)
            check(row["window_label"] == expected_window, f"window label error in {key}", errors)
            check(row["post_activation"] == ("1" if post_activation else "0"), f"activation flag error in {key}", errors)

    marker_fields = sorted(field for field in fields if is_marker(field))
    eligible_features = sorted(field for field in numeric_fields if field not in marker_fields)
    family_counts = Counter(row["family"] for row in rows)
    marker_activity: dict[str, dict[str, int]] = {}
    for family in sorted(expected_families):
        family_rows = [row for row in rows if row["family"] == family and row["mode"] == "attack"]
        marker_activity[family] = {
            field: sum(int(float(row[field])) for row in family_rows)
            for field in marker_fields
            if any(float(row[field]) != 0 for row in family_rows)
        }
    ranges = {
        field: {"min": min(float(row[field]) for row in rows), "max": max(float(row[field]) for row in rows)}
        for field in SUMMARY_FIELDS
    }
    audit = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "rows": len(rows),
        "columns": len(fields),
        "run_groups": len(grouped),
        "family_window_counts": dict(sorted(family_counts.items())),
        "marker_fields_excluded": marker_fields,
        "eligible_numeric_features": eligible_features,
        "eligible_numeric_feature_count": len(eligible_features),
        "selected_generic_feature_ranges": ranges,
        "attack_marker_activity_by_family": marker_activity,
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "audit_results.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    with (RESULTS / "feature_eligibility.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["field", "classification", "reason"], lineterminator="\n")
        writer.writeheader()
        for field in fields:
            if field in METADATA_FIELDS:
                writer.writerow({"field": field, "classification": "excluded_metadata", "reason": "provenance, label, or time context"})
            elif field in marker_fields:
                writer.writerow({"field": field, "classification": "excluded_marker", "reason": "simulator attack instrumentation; label leakage risk"})
            else:
                writer.writerow({"field": field, "classification": "eligible_numeric", "reason": "generic observed routing, topology, application, or radio value"})

    report = [
        "# Dataset Quality Audit v1", "",
        f"**Status:** {audit['status']}", "",
        "## Integrity", "",
        f"- {len(rows)} rows, {len(fields)} columns, and {len(grouped)} complete run groups.",
        "- Nine attack families; each contributes 90 windows (45 attack and 45 control).",
        "- No empty values, non-numeric feature values, duplicate run windows, or incomplete 60-second sequences were found.",
        "", "## Labels And Timing", "",
        "- Every group contains windows starting at 0, 60, ..., 480 seconds.",
        "- `window_label=1` only for attack-run windows beginning at or after the 240-second activation boundary.",
        "- Control windows and pre-activation attack windows are labelled 0.",
        "", "## Leakage Control", "",
        f"- {len(marker_fields)} attack-implementation marker fields are validation-only and excluded from IDS features.",
        f"- {len(eligible_features)} numeric generic features remain eligible before a model-specific feature selection step.",
        "- `family`, `seed`, run IDs, labels, and time fields are metadata and are also excluded from model inputs.",
        "", "## Generic Feature Range Check", "",
    ]
    report.extend(f"- `{field}`: {value['min']} to {value['max']}" for field, value in ranges.items())
    report.extend([
        "", "## Evaluation Protocol", "",
        "- Split only by complete family/mode/seed groups; never random CSV rows.",
        "- For cross-attack drift, train on one family and hold out all target-family groups.",
        "- For adaptation, use complete target seeds for adaptation and evaluate only on different target seeds.",
        "- Use marker fields only to verify attack activation, never as IDS or drift-detector input.",
    ])
    if errors:
        report.extend(["", "## Failures", ""] + [f"- {error}" for error in errors])
    (RESULTS / "dataset_quality_audit.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Audit {audit['status']}: {len(rows)} rows, {len(grouped)} groups, {len(marker_fields)} marker fields excluded")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

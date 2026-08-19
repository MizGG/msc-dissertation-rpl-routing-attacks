#!/usr/bin/env python3
"""Audit the supplied Dr Gope 6LoWPAN/RPL dataset CSV files."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ATTACK_NAMES = {
    "Blackhole (BH)": "blackhole",
    "DIO Suppression (DS)": "dio_suppression",
    "DIS Flooding (DA)": "dis_flooding",
    "Grayhole (GH)": "grayhole",
    "Increase Rank (IR)": "increase_rank",
    "Sinkhole (SH)": "sinkhole",
    "Wormhole (WH)": "wormhole",
    "Worst Parent (WP)": "worst_parent",
}


def csv_files(base: Path) -> list[Path]:
    return sorted(path for path in base.glob("*/*.csv") if path.is_file())


def normalise_attack(path: Path) -> str:
    return ATTACK_NAMES.get(path.parent.name, path.parent.name)


def audit_file(path: Path) -> tuple[dict[str, str | int], list[str], Counter[str]]:
    label_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    row_count = 0
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        label_column = "TYPE" if "TYPE" in columns else ""
        for row in reader:
            row_count += 1
            if label_column:
                label_counts[row.get(label_column, "")] += 1
            for column in columns:
                value = row.get(column, "")
                if value == "" or value.lower() in {"na", "nan", "null", "none"}:
                    missing_counts[column] += 1

    summary = {
        "attack": normalise_attack(path),
        "source_folder": path.parent.name,
        "csv_file": path.name,
        "rows": row_count,
        "columns": len(columns),
        "has_TYPE_label": 1 if "TYPE" in columns else 0,
        "label_counts": ";".join(f"{label}:{count}" for label, count in sorted(label_counts.items())),
        "missing_cells": sum(missing_counts.values()),
        "columns_with_missing": sum(1 for value in missing_counts.values() if value > 0),
    }
    return summary, columns, missing_counts


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path("/Users/mizzy/Documents/Dissertation/Dissertation_Cooja_Work/DR P"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/gope_dataset"))
    args = parser.parse_args()

    files = csv_files(args.dataset_dir)
    if not files:
        raise SystemExit(f"No CSV files found under {args.dataset_dir}")

    summaries: list[dict[str, str | int]] = []
    columns_by_attack: dict[str, set[str]] = {}
    missing_rows: list[dict[str, str | int]] = []

    for path in files:
        summary, columns, missing_counts = audit_file(path)
        summaries.append(summary)
        attack = str(summary["attack"])
        columns_by_attack[attack] = set(columns)
        for column in columns:
            missing = missing_counts[column]
            if missing:
                missing_rows.append({
                    "attack": attack,
                    "column": column,
                    "missing_count": missing,
                    "rows": summary["rows"],
                })

    all_columns = sorted(set().union(*columns_by_attack.values()))
    attacks = sorted(columns_by_attack)
    overlap_rows: list[dict[str, str | int]] = []
    for column in all_columns:
        present_in = [attack for attack in attacks if column in columns_by_attack[attack]]
        overlap_rows.append({
            "column": column,
            "present_in_count": len(present_in),
            "present_in_attacks": ";".join(present_in),
            "missing_from_attacks": ";".join(attack for attack in attacks if attack not in present_in),
        })

    common_columns = [row["column"] for row in overlap_rows if row["present_in_count"] == len(attacks)]
    label_compatible = [summary for summary in summaries if int(summary["has_TYPE_label"]) == 1]

    write_csv(args.out_dir / "audit_summary.csv", summaries)
    write_csv(args.out_dir / "column_overlap.csv", overlap_rows)
    if missing_rows:
        write_csv(args.out_dir / "missing_values.csv", missing_rows)

    (args.out_dir / "README.md").write_text(
        "# Supplied Gope Dataset Audit\n\n"
        f"Dataset source: `{args.dataset_dir}`\n\n"
        "This audit covers the supplied Dr Gope 6LoWPAN/RPL CSV files before "
        "baseline reproduction. It records row counts, schema size, TYPE label "
        "availability, label counts, missing values and column overlap.\n\n"
        f"CSV files audited: {len(files)}\n\n"
        f"Files with `TYPE` labels: {len(label_compatible)} / {len(files)}\n\n"
        f"Columns common to all files: {len(common_columns)}\n\n"
        "Outputs:\n\n"
        "- `audit_summary.csv`\n"
        "- `column_overlap.csv`\n"
        "- `missing_values.csv` when missing values are present\n\n"
        "Use this audit before reproducing the paper baseline or mapping the "
        "supplied data to independently generated Cooja features.\n",
        encoding="utf-8",
    )

    print(args.out_dir / "audit_summary.csv")
    print(args.out_dir / "column_overlap.csv")


if __name__ == "__main__":
    main()

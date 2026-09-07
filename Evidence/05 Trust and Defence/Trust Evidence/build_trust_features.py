#!/usr/bin/env python3
"""Build trust-aware features from existing routing-window CSVs."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


DEFAULT_INPUTS = [
    Path("experiments/cross_attack_drift_v1/features/bh_sh_routing_window_features.csv"),
    Path("experiments/cross_attack_drift_v1/features/additional_routing_window_features.csv"),
    Path("experiments/sybil_attack_v1/features/routing_window_features.csv"),
]

TRUST_FIELDS = [
    "trust_forwarding",
    "trust_rank",
    "trust_control",
    "trust_route",
    "trust_total",
    "trust_penalised",
    "trust_forwarding_alert",
    "trust_rank_alert",
    "trust_control_alert",
    "trust_route_alert",
    "trust_any_alert",
]


def read_rows(paths: list[Path]) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    fields: list[str] = []
    seen: set[str] = set()
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for field in reader.fieldnames or []:
                if field not in seen:
                    seen.add(field)
                    fields.append(field)
            rows.extend(reader)
    for row in rows:
        for field in fields:
            row.setdefault(field, "0")
    return rows, fields


def number(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, "0") or 0)
    except ValueError:
        return 0.0


def mean(values: list[float], default: float = 0.0) -> float:
    return statistics.mean(values) if values else default


def bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def excess_penalty(value: float, baseline: float, scale: float) -> float:
    excess = max(0.0, value - baseline)
    return min(1.0, excess / max(scale, 1.0))


def run_baselines(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    by_run: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_run.setdefault(row["run_id"], []).append(row)

    baselines: dict[str, dict[str, float]] = {}
    for run_id, run_rows in by_run.items():
        pre = [row for row in run_rows if number(row, "window_start_s") < 240]
        source = pre or run_rows
        baselines[run_id] = {
            "app_rx_delta": mean([number(row, "app_rx_delta") for row in source], 1.0),
            "dis_tx_count": mean([number(row, "dis_tx_count") for row in source], 0.0),
            "dio_tx_count": mean([number(row, "dio_tx_count") for row in source], 0.0),
            "dio_rx_count": mean([number(row, "dio_rx_count") for row in source], 0.0),
            "dao_tx_count": mean([number(row, "dao_tx_count") for row in source], 0.0),
            "unique_dio_senders": mean([number(row, "unique_dio_senders") for row in source], 0.0),
            "parent_switch_count": mean([number(row, "parent_switch_count") for row in source], 0.0),
            "topology_mean_depth": mean([number(row, "topology_mean_depth") for row in source], 0.0),
        }
    return baselines


def add_trust(row: dict[str, str], baseline: dict[str, float]) -> None:
    rx = number(row, "app_rx_delta")
    expected_rx = max(baseline["app_rx_delta"], 1.0)
    forwarding_loss = max(0.0, expected_rx - rx) / expected_rx
    missed = number(row, "app_missed_delta")
    missed_pressure = min(1.0, missed / max(rx + missed, 1.0))
    trust_forwarding = bounded(1.0 - min(1.0, 0.85 * forwarding_loss + 0.15 * missed_pressure))

    low_rank = number(row, "dio_rx_low_rank_nonroot_count") + number(row, "state_low_rank_nonroot_pairs")
    exposed = number(row, "state_receivers_exposed_low_rank_nonroot")
    rank_range = number(row, "dio_rx_nonroot_rank_range")
    rank_penalty = min(1.0, (low_rank / 8.0) + (exposed / 16.0) + (rank_range / 4096.0))
    trust_rank = bounded(1.0 - rank_penalty)

    control_penalty = 0.0
    control_penalty += 0.30 * excess_penalty(number(row, "dis_tx_count"), baseline["dis_tx_count"] + 2.0, 18.0)
    control_penalty += 0.20 * excess_penalty(number(row, "dio_tx_count"), baseline["dio_tx_count"] + 2.0, 12.0)
    control_penalty += 0.15 * excess_penalty(number(row, "dio_rx_count"), baseline["dio_rx_count"] + 10.0, 80.0)
    control_penalty += 0.15 * excess_penalty(number(row, "dao_tx_count"), baseline["dao_tx_count"] + 2.0, 12.0)
    control_penalty += 0.20 * excess_penalty(number(row, "unique_dio_senders"), baseline["unique_dio_senders"] + 2.0, 16.0)
    trust_control = bounded(1.0 - min(1.0, control_penalty))

    route_penalty = 0.0
    route_penalty += 0.45 * excess_penalty(number(row, "parent_switch_count"), baseline["parent_switch_count"] + 1.0, 6.0)
    route_penalty += 0.25 * min(1.0, number(row, "no_parent_events") / 8.0)
    route_penalty += 0.15 * excess_penalty(number(row, "topology_mean_depth"), baseline["topology_mean_depth"] + 1.0, 4.0)
    route_penalty += 0.15 * min(1.0, number(row, "topology_max_depth") / 10.0)
    trust_route = bounded(1.0 - min(1.0, route_penalty))

    trust_total = bounded(
        0.40 * trust_forwarding
        + 0.25 * trust_rank
        + 0.20 * trust_control
        + 0.15 * trust_route
    )

    row["trust_forwarding"] = f"{trust_forwarding:.4f}"
    row["trust_rank"] = f"{trust_rank:.4f}"
    row["trust_control"] = f"{trust_control:.4f}"
    row["trust_route"] = f"{trust_route:.4f}"
    row["trust_total"] = f"{trust_total:.4f}"
    forwarding_alert = trust_forwarding < 0.82
    rank_alert = trust_rank < 0.70
    control_alert = trust_control < 0.85
    route_alert = trust_route < 0.70
    any_alert = forwarding_alert or rank_alert or control_alert or route_alert or trust_total < 0.70

    row["trust_penalised"] = "1" if trust_total < 0.60 else "0"
    row["trust_forwarding_alert"] = "1" if forwarding_alert else "0"
    row["trust_rank_alert"] = "1" if rank_alert else "0"
    row["trust_control_alert"] = "1" if control_alert else "0"
    row["trust_route_alert"] = "1" if route_alert else "0"
    row["trust_any_alert"] = "1" if any_alert else "0"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", type=Path, default=DEFAULT_INPUTS)
    parser.add_argument("--out", type=Path, default=Path("experiments/trust_layer_v1/features/trust_routing_window_features.csv"))
    args = parser.parse_args()

    rows, fields = read_rows(args.inputs)
    baselines = run_baselines(rows)
    for row in rows:
        add_trust(row, baselines[row["run_id"]])

    output_fields = fields + [field for field in TRUST_FIELDS if field not in fields]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} trust-enhanced windows to {args.out}")


if __name__ == "__main__":
    main()

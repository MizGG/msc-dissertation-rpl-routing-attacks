#!/usr/bin/env python3
"""Extract generic RPL routing telemetry into seed-safe 60-second windows."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


TIME_RE = re.compile(r"^(?P<mm>\d+):(?P<ss>\d\d)\.(?P<ms>\d{3})")
RUN_RE = re.compile(r"(?P<family>BH|SH|DIS_FLOOD|GRAYHOLE|INCREASE_RANK|DIO_SUPPRESSION|WORST_PARENT|WORMHOLE)_(?P<mode>ATTACK|CONTROL)_N(?P<nodes>\d+)_SEED(?P<seed>\d+)")
APP_RE = re.compile(r"ID:(?P<node>\d+).*Tx/Rx/MissedTx: (?P<tx>\d+)/(?P<rx>\d+)/(?P<missed>\d+)")
DIO_RX_RE = re.compile(r"received a (?:multicast|unicast)-DIO from (?P<source>[^,]+),.* rank (?P<rank>\d+)$")
DIO_TX_RE = re.compile(r"sending a (?:multicast|unicast)-DIO with rank (?P<rank>\d+) to (?P<target>\S+)")
PARENT_SWITCH_RE = re.compile(r"parent switch: (?P<old>.+?) -> (?P<new>.+)$")
LOG_NODE_RE = re.compile(r"\bID:(?P<node>\d+)\b")
OWN_STATE_RE = re.compile(
    r"nbr: own state,.* rank (?P<rank>\d+) max-rank \d+, dioint \d+, nbr count (?P<count>\d+)"
)
TOPOLOGY_LINK_RE = re.compile(r"links: (?P<child>fd00::\S+)\s+to (?P<parent>fd00::\S+)")

FAMILY_NAMES = {
    "BH": "blackhole",
    "SH": "sinkhole",
    "DIS_FLOOD": "dis_flood",
    "GRAYHOLE": "grayhole",
    "INCREASE_RANK": "increase_rank",
    "DIO_SUPPRESSION": "dio_suppression",
    "WORST_PARENT": "worst_parent",
    "WORMHOLE": "wormhole",
}


def seconds_from_text(text: str) -> float | None:
    match = TIME_RE.match(text)
    if match is None:
        return None
    return int(match.group("mm")) * 60 + int(match.group("ss")) + int(match.group("ms")) / 1000


def window_index(seconds: float, width: int, duration: int) -> int | None:
    return int(seconds // width) if 0 <= seconds < duration else None


def node_id_from_addr(address: str) -> int | None:
    text = address.strip()
    if ":" not in text or "NULL" in text:
        return None
    try:
        return int(text.rsplit(":", maxsplit=1)[1], 16)
    except ValueError:
        return None


def empty_window(run_id: str, family: str, mode: str, seed: str, nodes: str, start: int, width: int) -> dict[str, object]:
    return {
        "run_id": run_id,
        "family": family,
        "mode": mode.lower(),
        "binary_run_label": 1 if mode == "ATTACK" else 0,
        "window_label": 1 if mode == "ATTACK" and start >= 240 else 0,
        "nodes": int(nodes),
        "seed": seed,
        "window_start_s": start,
        "window_end_s": start + width,
        "post_activation": 1 if start >= 240 else 0,
        "app_tx_delta": 0,
        "app_rx_delta": 0,
        "app_missed_delta": 0,
        "app_reporting_nodes": 0,
        "radio_tx_count": 0,
        "radio_bytes": 0,
        "radio_interfered_count": 0,
        "unique_radio_senders": 0,
        "attacker_node16_radio_tx": 0,
        "root_node1_radio_tx": 0,
        "dio_rx_count": 0,
        "dio_tx_count": 0,
        "dis_rx_count": 0,
        "dis_tx_count": 0,
        "dao_rx_count": 0,
        "dao_tx_count": 0,
        "parent_switch_count": 0,
        "parent_switch_to_root_count": 0,
        "parent_switch_to_nonroot_count": 0,
        "unique_parent_targets": 0,
        "parent_found_events": 0,
        "no_parent_events": 0,
        "significant_rank_update_count": 0,
        "unique_dio_senders": 0,
        "unique_dio_receivers": 0,
        "dio_rx_rank_min": 0.0,
        "dio_rx_rank_mean": 0.0,
        "dio_rx_rank_max": 0.0,
        "dio_rx_rank_range": 0.0,
        "dio_rx_nonroot_count": 0,
        "dio_rx_nonroot_rank_min": 0.0,
        "dio_rx_nonroot_rank_mean": 0.0,
        "dio_rx_nonroot_rank_max": 0.0,
        "dio_rx_nonroot_rank_range": 0.0,
        "dio_rx_low_rank_nonroot_count": 0,
        "unique_low_rank_nonroot_senders": 0,
        "dio_tx_rank_mean": 0.0,
        "state_nonroot_rank_min": 0.0,
        "state_nonroot_rank_mean": 0.0,
        "state_nonroot_rank_max": 0.0,
        "state_nonroot_rank_range": 0.0,
        "state_low_rank_nonroot_pairs": 0,
        "state_low_rank_nonroot_senders": 0,
        "state_receivers_exposed_low_rank_nonroot": 0,
        "own_state_sample_count": 0,
        "own_rank_min": 0.0,
        "own_rank_mean": 0.0,
        "own_rank_max": 0.0,
        "own_rank_range": 0.0,
        "own_neighbor_count_mean": 0.0,
        "own_neighbor_count_max": 0,
        "topology_edge_count": 0,
        "topology_unique_parents": 0,
        "topology_max_parent_fanout": 0,
        "topology_root_direct_children": 0,
        "topology_mean_depth": 0.0,
        "topology_max_depth": 0,
        "sinkhole_attack_enabled_events": 0,
        "sinkhole_advertised_rank_events": 0,
        "blackhole_attack_enabled_events": 0,
        "blackhole_drop_events": 0,
        "grayhole_attack_enabled_events": 0,
        "grayhole_drop_events": 0,
        "increase_rank_attack_enabled_events": 0,
        "increase_rank_advertised_rank_events": 0,
        "dis_flood_attack_enabled_events": 0,
        "dis_flood_sent_events": 0,
        "dio_suppression_attack_enabled_events": 0,
        "dio_suppression_events": 0,
        "worst_parent_attack_enabled_events": 0,
        "worst_parent_selection_events": 0,
        "wormhole_attack_enabled_events": 0,
        "wormhole_endpoint_radio_events": 0,
    }


def set_rank_stats(row: dict[str, object], prefix: str, values: list[int]) -> None:
    if not values:
        return
    row[f"{prefix}_min"] = min(values)
    row[f"{prefix}_mean"] = round(sum(values) / len(values), 4)
    row[f"{prefix}_max"] = max(values)
    row[f"{prefix}_range"] = max(values) - min(values)


def parse_run(run_dir: Path, width: int, duration: int, root_node: int) -> list[dict[str, object]]:
    match = RUN_RE.fullmatch(run_dir.name)
    if match is None:
        raise ValueError(f"Unexpected run directory name: {run_dir.name}")
    family = FAMILY_NAMES[match.group("family")]
    mode = match.group("mode")
    windows = [
        empty_window(run_dir.name, family, mode, match.group("seed"), match.group("nodes"), start, width)
        for start in range(0, duration, width)
    ]
    app_stats: dict[str, list[tuple[float, int, int, int]]] = defaultdict(list)
    radio_senders = [set() for _ in windows]
    parent_targets = [set() for _ in windows]
    dio_senders = [set() for _ in windows]
    dio_receivers = [set() for _ in windows]
    low_rank_senders = [set() for _ in windows]
    dio_ranks: list[list[int]] = [[] for _ in windows]
    dio_nonroot_ranks: list[list[int]] = [[] for _ in windows]
    dio_tx_ranks: list[list[int]] = [[] for _ in windows]
    dio_observations: list[list[tuple[float, int, int, int]]] = [[] for _ in windows]
    own_ranks: list[list[int]] = [[] for _ in windows]
    own_neighbor_counts: list[list[int]] = [[] for _ in windows]
    topology_edges: list[list[tuple[int, int]]] = [[] for _ in windows]

    with (run_dir / "COOJA.testlog").open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            seconds = seconds_from_text(line)
            idx = window_index(seconds, width, duration) if seconds is not None else None
            if idx is None:
                continue
            row = windows[idx]
            node_match = LOG_NODE_RE.search(line)
            receiver = int(node_match.group("node")) if node_match else None
            app_match = APP_RE.search(line)
            if app_match:
                app_stats[app_match.group("node")].append((
                    seconds,
                    int(app_match.group("tx")),
                    int(app_match.group("rx")),
                    int(app_match.group("missed")),
                ))

            dio_rx = DIO_RX_RE.search(line.rstrip())
            if dio_rx:
                rank = int(dio_rx.group("rank"))
                source = node_id_from_addr(dio_rx.group("source"))
                row["dio_rx_count"] = int(row["dio_rx_count"]) + 1
                dio_ranks[idx].append(rank)
                if source is not None:
                    dio_senders[idx].add(source)
                if receiver is not None:
                    dio_receivers[idx].add(receiver)
                if source is not None and receiver is not None:
                    dio_observations[idx].append((seconds, receiver, source, rank))
                if source is not None and source != root_node:
                    row["dio_rx_nonroot_count"] = int(row["dio_rx_nonroot_count"]) + 1
                    dio_nonroot_ranks[idx].append(rank)
                    if rank <= 128:
                        row["dio_rx_low_rank_nonroot_count"] = int(row["dio_rx_low_rank_nonroot_count"]) + 1
                        low_rank_senders[idx].add(source)

            dio_tx = DIO_TX_RE.search(line)
            if dio_tx:
                row["dio_tx_count"] = int(row["dio_tx_count"]) + 1
                dio_tx_ranks[idx].append(int(dio_tx.group("rank")))
            if "received a DIS from" in line:
                row["dis_rx_count"] = int(row["dis_rx_count"]) + 1
            if "sending a DIS to" in line:
                row["dis_tx_count"] = int(row["dis_tx_count"]) + 1
            if "received a DAO from" in line or "received a No-path DAO from" in line:
                row["dao_rx_count"] = int(row["dao_rx_count"]) + 1
            if "sending a DAO" in line or "sending a No-path DAO" in line:
                row["dao_tx_count"] = int(row["dao_tx_count"]) + 1

            parent_switch = PARENT_SWITCH_RE.search(line.rstrip())
            if parent_switch:
                target = node_id_from_addr(parent_switch.group("new"))
                row["parent_switch_count"] = int(row["parent_switch_count"]) + 1
                if target is not None:
                    parent_targets[idx].add(target)
                    field = "parent_switch_to_root_count" if target == root_node else "parent_switch_to_nonroot_count"
                    row[field] = int(row[field]) + 1
            if "found parent:" in line:
                row["parent_found_events"] = int(row["parent_found_events"]) + 1
            if "no parent" in line:
                row["no_parent_events"] = int(row["no_parent_events"]) + 1
            if "significant rank update" in line:
                row["significant_rank_update_count"] = int(row["significant_rank_update_count"]) + 1

            own_state = OWN_STATE_RE.search(line)
            if own_state:
                own_ranks[idx].append(int(own_state.group("rank")))
                own_neighbor_counts[idx].append(int(own_state.group("count")))
            topology_link = TOPOLOGY_LINK_RE.search(line)
            if topology_link:
                child = node_id_from_addr(topology_link.group("child"))
                parent = node_id_from_addr(topology_link.group("parent"))
                if child is not None and parent is not None:
                    topology_edges[idx].append((child, parent))

            for marker, field in (
                ("SINKHOLE ATTACK: enabled", "sinkhole_attack_enabled_events"),
                ("SINKHOLE: advertising rank", "sinkhole_advertised_rank_events"),
                ("BLACKHOLE ATTACK: enabled", "blackhole_attack_enabled_events"),
                ("BLACKHOLE: dropping forwarded packet", "blackhole_drop_events"),
                ("GRAYHOLE ATTACK: enabled", "grayhole_attack_enabled_events"),
                ("GRAYHOLE: dropping forwarded packet", "grayhole_drop_events"),
                ("INCREASE RANK ATTACK: enabled", "increase_rank_attack_enabled_events"),
                ("INCREASE_RANK: advertising rank", "increase_rank_advertised_rank_events"),
                ("DIS FLOOD ATTACK: enabled", "dis_flood_attack_enabled_events"),
                ("DIS FLOOD ATTACK: sent multicast DIS", "dis_flood_sent_events"),
                ("DIO SUPPRESSION ATTACK: enabled", "dio_suppression_attack_enabled_events"),
                ("DIO SUPPRESSION: suppressing outgoing DIO", "dio_suppression_events"),
                ("WORST PARENT ATTACK: enabled", "worst_parent_attack_enabled_events"),
                ("WORST PARENT: selecting acceptable parent", "worst_parent_selection_events"),
                ("WORMHOLE ATTACK: tunnel enabled between 16 and 17", "wormhole_attack_enabled_events"),
            ):
                if marker in line:
                    row[field] = int(row[field]) + 1

    for samples in app_stats.values():
        samples.sort()
        for previous, current in zip(samples, samples[1:]):
            idx = window_index(current[0], width, duration)
            if idx is None:
                continue
            windows[idx]["app_tx_delta"] = int(windows[idx]["app_tx_delta"]) + max(0, current[1] - previous[1])
            windows[idx]["app_rx_delta"] = int(windows[idx]["app_rx_delta"]) + max(0, current[2] - previous[2])
            windows[idx]["app_missed_delta"] = int(windows[idx]["app_missed_delta"]) + max(0, current[3] - previous[3])
            windows[idx]["app_reporting_nodes"] = int(windows[idx]["app_reporting_nodes"]) + 1

    with (run_dir / "COOJA.radio").open(encoding="utf-8", errors="replace") as handle:
        next(handle, None)
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 6:
                continue
            seconds = seconds_from_text(parts[1])
            idx = window_index(seconds, width, duration) if seconds is not None else None
            if idx is None:
                continue
            sender = parts[2]
            windows[idx]["radio_tx_count"] = int(windows[idx]["radio_tx_count"]) + 1
            windows[idx]["radio_bytes"] = int(windows[idx]["radio_bytes"]) + int(parts[4])
            windows[idx]["radio_interfered_count"] = int(windows[idx]["radio_interfered_count"]) + int(parts[5])
            radio_senders[idx].add(sender)
            if sender == "16":
                windows[idx]["attacker_node16_radio_tx"] = int(windows[idx]["attacker_node16_radio_tx"]) + 1
            if sender == str(root_node):
                windows[idx]["root_node1_radio_tx"] = int(windows[idx]["root_node1_radio_tx"]) + 1
            destinations = set(parts[3].split(","))
            if seconds is not None and seconds >= 240:
                if sender == "16" and "17" in destinations:
                    windows[idx]["wormhole_endpoint_radio_events"] = int(windows[idx]["wormhole_endpoint_radio_events"]) + 1
                elif sender == "17" and "16" in destinations:
                    windows[idx]["wormhole_endpoint_radio_events"] = int(windows[idx]["wormhole_endpoint_radio_events"]) + 1

    latest_rank_by_pair: dict[tuple[int, int], int] = {}
    for idx, row in enumerate(windows):
        for _, receiver, source, rank in sorted(dio_observations[idx]):
            latest_rank_by_pair[(receiver, source)] = rank
        row["unique_radio_senders"] = len(radio_senders[idx])
        row["unique_parent_targets"] = len(parent_targets[idx])
        row["unique_dio_senders"] = len(dio_senders[idx])
        row["unique_dio_receivers"] = len(dio_receivers[idx])
        row["unique_low_rank_nonroot_senders"] = len(low_rank_senders[idx])
        set_rank_stats(row, "dio_rx_rank", dio_ranks[idx])
        set_rank_stats(row, "dio_rx_nonroot_rank", dio_nonroot_ranks[idx])
        if dio_tx_ranks[idx]:
            row["dio_tx_rank_mean"] = round(sum(dio_tx_ranks[idx]) / len(dio_tx_ranks[idx]), 4)
        state_nonroot_ranks = [
            rank for (_, source), rank in latest_rank_by_pair.items() if source != root_node
        ]
        set_rank_stats(row, "state_nonroot_rank", state_nonroot_ranks)
        low_rank_pairs = [
            (receiver, source)
            for (receiver, source), rank in latest_rank_by_pair.items()
            if source != root_node and rank <= 128
        ]
        row["state_low_rank_nonroot_pairs"] = len(low_rank_pairs)
        row["state_low_rank_nonroot_senders"] = len({source for _, source in low_rank_pairs})
        row["state_receivers_exposed_low_rank_nonroot"] = len({receiver for receiver, _ in low_rank_pairs})
        if own_ranks[idx]:
            row["own_state_sample_count"] = len(own_ranks[idx])
            set_rank_stats(row, "own_rank", own_ranks[idx])
            row["own_neighbor_count_mean"] = round(
                sum(own_neighbor_counts[idx]) / len(own_neighbor_counts[idx]), 4
            )
            row["own_neighbor_count_max"] = max(own_neighbor_counts[idx])
        if topology_edges[idx]:
            parent_by_child = dict(topology_edges[idx])
            fanout: dict[int, int] = defaultdict(int)
            for parent in parent_by_child.values():
                fanout[parent] += 1
            depths: list[int] = []
            for child in parent_by_child:
                current = child
                seen: set[int] = set()
                depth = 0
                while current != root_node and current in parent_by_child and current not in seen:
                    seen.add(current)
                    current = parent_by_child[current]
                    depth += 1
                if current == root_node:
                    depths.append(depth)
            row["topology_edge_count"] = len(parent_by_child)
            row["topology_unique_parents"] = len(fanout)
            row["topology_max_parent_fanout"] = max(fanout.values())
            row["topology_root_direct_children"] = fanout.get(root_node, 0)
            if depths:
                row["topology_mean_depth"] = round(sum(depths) / len(depths), 4)
                row["topology_max_depth"] = max(depths)
    return windows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", type=Path, default=Path("experiments/routing_features_v1/runs"))
    parser.add_argument("--out", type=Path, default=Path("experiments/routing_features_v1/features/routing_window_features.csv"))
    parser.add_argument("--window", type=int, default=60)
    parser.add_argument("--duration", type=int, default=540)
    parser.add_argument("--root-node", type=int, default=1)
    parser.add_argument("--expected-runs", type=int, default=20)
    args = parser.parse_args()

    run_dirs = sorted(path for path in args.runs_dir.iterdir() if path.is_dir())
    complete = [path for path in run_dirs if (path / "COOJA.testlog").is_file() and (path / "COOJA.radio").is_file()]
    if args.expected_runs and len(complete) != args.expected_runs:
        raise ValueError(f"Expected {args.expected_runs} complete routing-feature runs; found {len(complete)}")
    rows: list[dict[str, object]] = []
    for run_dir in complete:
        rows.extend(parse_run(run_dir, args.window, args.duration, args.root_node))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} windows from {len(complete)} runs to {args.out}")


if __name__ == "__main__":
    main()

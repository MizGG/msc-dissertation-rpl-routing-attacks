#!/usr/bin/env python3
"""Reproducible external validation for the MSc RPL IDS study.

This program deliberately keeps all raw external data untouched.  It creates
window-level derivative data and evaluates the same *static versus adapted*
question used in the Cooja work, but never claims raw-feature equivalence across
simulators.  RADAR is NetSim packet traffic, UOS is Cooja packet traffic, and
HUNSR is pre-engineered Contiki-NG node-behaviour data.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT
OUT = ROOT / "results"
DERIVED = ROOT / "derived_data"
WINDOW_SECONDS = 60
RADAR_START = re.compile(r"^(\d+):.*Attack start time:\s*([0-9.]+)")


def number(value: object) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


def metric_row(name: str, dataset: str, model_name: str, train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> dict[str, object]:
    if train.empty or test.empty or train["label"].nunique() != 2 or test["label"].nunique() != 2:
        raise ValueError(f"{name}: both classes are required in train and test")
    # Packet datasets can contain unusually large counters.  Bound numerical
    # values before scaling so a single malformed/cumulative counter cannot
    # destabilise logistic optimisation.  The same transformation is fitted
    # and applied inside each test; no labels are used by it.
    bounded = FunctionTransformer(lambda x: np.clip(np.nan_to_num(x, nan=0.0, posinf=1_000_000.0, neginf=-1_000_000.0), -1_000_000.0, 1_000_000.0))
    models = {
        "logistic": Pipeline([
            ("bound", bounded),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42)),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=8, min_samples_leaf=2,
            class_weight="balanced", random_state=42, n_jobs=-1,
        ),
    }
    model = models[model_name]
    model.fit(train[features], train["label"])
    prediction = model.predict(test[features])
    return {
        "dataset": dataset,
        "experiment": name,
        "model": model_name,
        "features": len(features),
        "train_windows": len(train),
        "test_windows": len(test),
        "attack_train": int(train["label"].sum()),
        "attack_test": int(test["label"].sum()),
        "accuracy": round(float(accuracy_score(test["label"], prediction)), 4),
        "precision": round(float(precision_score(test["label"], prediction, zero_division=0)), 4),
        "recall": round(float(recall_score(test["label"], prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(test["label"], prediction, zero_division=0)), 4),
    }


def write_csv(path: Path, data: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)


def finalise_windows(windows: dict[tuple[str, int], dict[str, object]]) -> pd.DataFrame:
    output: list[dict[str, object]] = []
    for (group, window), values in windows.items():
        packet_count = int(values["packet_count"])
        rank_values = values["rank_values"]
        lengths = values["lengths"]
        output.append({
            "group": group,
            "window": window,
            "label": int(values["label"]),
            "packet_count": packet_count,
            "control_packets": int(values["control_packets"]),
            "dio_count": int(values["dio_count"]),
            "dis_count": int(values["dis_count"]),
            "dao_count": int(values["dao_count"]),
            "app_packets": int(values["app_packets"]),
            "unique_sources": len(values["sources"]),
            "unique_destinations": len(values["destinations"]),
            "unique_transmitters": len(values["transmitters"]),
            "unique_receivers": len(values["receivers"]),
            "mean_payload_bytes": round(sum(lengths) / len(lengths), 4) if lengths else 0.0,
            "mean_rank": round(sum(rank_values) / len(rank_values), 4) if rank_values else 0.0,
            "rank_range": round(max(rank_values) - min(rank_values), 4) if rank_values else 0.0,
            "rank_observations": len(rank_values),
        })
    return pd.DataFrame(output)


def new_window(label: int) -> dict[str, object]:
    return {
        "label": label, "packet_count": 0, "control_packets": 0,
        "dio_count": 0, "dis_count": 0, "dao_count": 0, "app_packets": 0,
        "sources": set(), "destinations": set(), "transmitters": set(), "receivers": set(),
        "lengths": [], "rank_values": [],
    }


def radar_attack_starts(folder: Path) -> dict[str, float]:
    starts: dict[str, float] = {}
    for line in (folder / "attacks_start_time.txt").read_text(errors="replace").splitlines():
        match = RADAR_START.search(line)
        if match:
            starts[match.group(1)] = float(match.group(2)) / 1_000_000.0
    return starts


def build_radar() -> pd.DataFrame:
    cached = DERIVED / "radar_60s_windows.csv"
    if cached.exists():
        return pd.read_csv(cached)
    base = RAW / "RADAR_RPL_Attacks" / "RADAR" / "16_Nodes_Dataset"
    windows: dict[tuple[str, int], dict[str, object]] = {}
    for family in ("Legitimate", "Blackhole", "Sybil"):
        folder = base / family / "Packet_Trace_1500s"
        starts = {} if family == "Legitimate" else radar_attack_starts(folder)
        for path in sorted(folder.glob("*.csv")):
            group = f"{family.lower()}_{path.stem}"
            start = starts.get(path.stem, -math.inf)
            with path.open(newline="", encoding="utf-8", errors="replace") as handle:
                for row in csv.DictReader(handle):
                    time_us = number(row.get("PHY_LAYER_START_TIME(US)")) or number(row.get("NW_LAYER_ARRIVAL_TIME(US)"))
                    if not time_us:
                        continue
                    time_s = time_us / 1_000_000.0
                    # Attack traces have a benign warm-up.  Retain only post-start attack windows.
                    if family != "Legitimate" and time_s < start:
                        continue
                    label = 0 if family == "Legitimate" else 1
                    key = (group, int(time_s // WINDOW_SECONDS))
                    record = windows.setdefault(key, new_window(label))
                    record["packet_count"] += 1
                    packet_type = (row.get("PACKET_TYPE") or "").upper()
                    detail = (row.get("CONTROL_PACKET_TYPE/APP_NAME") or "").upper()
                    if "CONTROL" in packet_type:
                        record["control_packets"] += 1
                    if detail == "DIO": record["dio_count"] += 1
                    if detail == "DIS": record["dis_count"] += 1
                    if detail == "DAO": record["dao_count"] += 1
                    if "CONTROL" not in packet_type:
                        record["app_packets"] += 1
                    for field, target in (("SOURCE_ID", "sources"), ("DESTINATION_ID", "destinations"),
                                          ("TRANSMITTER_ID", "transmitters"), ("RECEIVER_ID", "receivers")):
                        value = row.get(field)
                        if value and value != "N/A": record[target].add(value)
                    payload = number(row.get("NW_LAYER_PAYLOAD(Bytes)"))
                    if payload: record["lengths"].append(payload)
                    rank = number(row.get("RPL_RANK"))
                    if rank: record["rank_values"].append(rank)
    data = finalise_windows(windows)
    data["family"] = data["group"].str.extract(r"^(legitimate|blackhole|sybil)_", expand=False)
    write_csv(DERIVED / "radar_60s_windows.csv", data)
    return data


def build_uos() -> pd.DataFrame:
    # The Git repository is a preview; the supplied RAR contains all 78 CSVs.
    base = RAW / "UOS_IOTSH_2024_full" / "UOS_IOTSH_2024 Dataset"
    windows: dict[tuple[str, int], dict[str, object]] = {}
    scenarios = [("1-Normal_Traffic", 0), ("2-Single_Attacker", 1), ("3-Dual_Attackers", 1)]
    for directory, label in scenarios:
        for path in sorted((base / directory).rglob("*.csv")):
            group = f"{directory}/{path.relative_to(base / directory)}"
            with path.open(newline="", encoding="utf-8", errors="replace") as handle:
                for row in csv.DictReader(handle):
                    time_s = number(row.get("Time"))
                    key = (group, int(time_s // WINDOW_SECONDS))
                    record = windows.setdefault(key, new_window(label))
                    record["packet_count"] += 1
                    protocol = (row.get("Protocol") or "").upper()
                    info = (row.get("Info") or "").upper()
                    if "RPL" in info or "ICMPV6" in protocol:
                        record["control_packets"] += 1
                    if "DODAG INFORMATION OBJECT" in info or "DIO" in info: record["dio_count"] += 1
                    if "DODAG INFORMATION SOLICITATION" in info or "DIS" in info: record["dis_count"] += 1
                    if "DESTINATION ADVERTISEMENT" in info or "DAO" in info: record["dao_count"] += 1
                    if "ICMPV6" not in protocol: record["app_packets"] += 1
                    for field, target in (("Source", "sources"), ("Destination", "destinations")):
                        value = row.get(field)
                        if value: record[target].add(value)
                    length = number(row.get("Length"))
                    if length: record["lengths"].append(length)
                    rank = number(row.get("Rank"))
                    if rank: record["rank_values"].append(rank)
    data = finalise_windows(windows)
    data["family"] = data["group"].str.split("/", n=1).str[0]
    write_csv(DERIVED / "uos_60s_windows.csv", data)
    return data


def split_by_groups(data: pd.DataFrame, test_groups: set[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    return data[~data.group.isin(test_groups)].copy(), data[data.group.isin(test_groups)].copy()


def radar_tests(data: pd.DataFrame) -> list[dict[str, object]]:
    features = [c for c in data.columns if c not in {"group", "window", "label", "family"}]
    normal = data[data.family == "legitimate"]
    normal_train, normal_test = split_by_groups(normal, {"legitimate_111", "legitimate_112", "legitimate_113", "legitimate_114", "legitimate_115"})
    bh = data[data.family == "blackhole"]
    sybil = data[data.family == "sybil"]
    bh_train, bh_test = split_by_groups(bh, {"blackhole_104", "blackhole_105"})
    sybil_train, sybil_test = split_by_groups(sybil, {"sybil_104", "sybil_105"})
    results: list[dict[str, object]] = []
    experiments = [
        ("in_domain_blackhole", pd.concat([normal_train, bh_train]), pd.concat([normal_test, bh_test])),
        ("in_domain_sybil", pd.concat([normal_train, sybil_train]), pd.concat([normal_test, sybil_test])),
        ("static_blackhole_to_sybil", pd.concat([normal_train, bh_train]), pd.concat([normal_test, sybil_test])),
        ("static_sybil_to_blackhole", pd.concat([normal_train, sybil_train]), pd.concat([normal_test, bh_test])),
        ("adapt_blackhole_to_sybil_20pct", pd.concat([normal_train, bh_train, sybil_train.sample(frac=0.20, random_state=42)]), pd.concat([normal_test, sybil_test])),
        ("adapt_sybil_to_blackhole_20pct", pd.concat([normal_train, sybil_train, bh_train.sample(frac=0.20, random_state=42)]), pd.concat([normal_test, bh_test])),
    ]
    for name, train, test in experiments:
        results.append(metric_row(name, "RADAR", "random_forest", train, test, features))
    return results


def uos_tests(data: pd.DataFrame) -> list[dict[str, object]]:
    normal = data[data.family == "1-Normal_Traffic"]
    single = data[data.family == "2-Single_Attacker"]
    dual = data[data.family == "3-Dual_Attackers"]
    # The published archive has only two readable normal-trace groups.  That is
    # adequate for schema inspection but not a defensible held-out IDS score.
    # Record the limitation instead of publishing a score from six normal windows.
    if normal.group.nunique() < 3 or len(normal) < 30:
        write_csv(DERIVED / "uos_data_adequacy.csv", pd.DataFrame([{
            "normal_groups": normal.group.nunique(), "normal_windows": len(normal),
            "single_attack_groups": single.group.nunique(), "single_attack_windows": len(single),
            "dual_attack_groups": dual.group.nunique(), "dual_attack_windows": len(dual),
            "decision": "No IDS score reported: insufficient independent normal traces for a valid held-out binary evaluation.",
        }]))
        return []
    features = [c for c in data.columns if c not in {"group", "window", "label", "family"}]
    # Deterministic disjoint files: suffix order gives held-out scenarios rather than row leakage.
    n_groups = sorted(normal.group.unique()); s_groups = sorted(single.group.unique()); d_groups = sorted(dual.group.unique())
    n_train, n_test = split_by_groups(normal, set(n_groups[-max(1, len(n_groups)//3):]))
    s_train, s_test = split_by_groups(single, set(s_groups[-max(1, len(s_groups)//3):]))
    d_train, d_test = split_by_groups(dual, set(d_groups[-max(1, len(d_groups)//3):]))
    results: list[dict[str, object]] = []
    experiments = [
        ("in_domain_single_sinkhole", pd.concat([n_train, s_train]), pd.concat([n_test, s_test])),
        ("in_domain_dual_sinkhole", pd.concat([n_train, d_train]), pd.concat([n_test, d_test])),
        ("static_single_to_dual_sinkhole", pd.concat([n_train, s_train]), pd.concat([n_test, d_test])),
        ("adapt_single_to_dual_sinkhole_20pct", pd.concat([n_train, s_train, d_train.sample(frac=0.20, random_state=42)]), pd.concat([n_test, d_test])),
    ]
    for name, train, test in experiments:
        results.append(metric_row(name, "UOS_IOTSH_2024", "random_forest", train, test, features))
    return results


def hun_sr_tests() -> list[dict[str, object]]:
    path = RAW / "HUNSR_RPL_IDS_Behavior" / "RPL-IDS-Beh.csv"
    data = pd.read_csv(path)
    data = data.rename(columns={"label": "source_label"})
    data["label"] = (data.source_label != 0).astype(int)
    # All released HUNSR behavioural fields are numeric. IDs and source label are excluded.
    features = [c for c in data.columns if c not in {"time_sec", "node_id", "parent_id", "source_label", "label"}]
    data = data.sort_values(["time_sec", "node_id"]).reset_index(drop=True)
    # 70/30 temporal split: avoids an optimistic random-row split.
    split = int(len(data) * 0.70)
    early, late = data.iloc[:split].copy(), data.iloc[split:].copy()
    normal_early, normal_late = early[early.source_label == 0], late[late.source_label == 0]
    normal_late = normal_late.copy()
    results: list[dict[str, object]] = []
    names = {1: "version_number", 2: "decreased_rank", 3: "dis_flood", 4: "selective_forwarding"}
    for attack, attack_name in names.items():
        src_early = early[early.source_label == attack]
        src_late = late[late.source_label == attack]
        if len(src_early) < 10 or len(src_late) < 10:
            continue
        train = pd.concat([normal_early, src_early])
        test = pd.concat([normal_late, src_late])
        results.append(metric_row(f"temporal_in_domain_{attack_name}", "HUNSR", "random_forest", train, test, features))
    # The source attack is VNA; target attacks are held out by type and time.
    source = early[early.source_label == 1]
    for target, target_name in {2: "decreased_rank", 3: "dis_flood", 4: "selective_forwarding"}.items():
        target_early = early[early.source_label == target]
        target_late = late[late.source_label == target]
        if target_early.empty or target_late.empty:
            continue
        static_train = pd.concat([normal_early, source])
        target_test = pd.concat([normal_late, target_late])
        adapted_train = pd.concat([static_train, target_early.sample(frac=0.20, random_state=42)])
        results.append(metric_row(f"static_version_to_{target_name}", "HUNSR", "random_forest", static_train, target_test, features))
        results.append(metric_row(f"adapt_version_to_{target_name}_20pct", "HUNSR", "random_forest", adapted_train, target_test, features))
    write_csv(DERIVED / "hunsr_temporal_binary_input_summary.csv", pd.DataFrame([{
        "rows": len(data), "features_used": len(features), "early_rows": len(early), "late_rows": len(late),
        "label_mapping": "0=Normal,1=VNA,2=DRA,3=DISA,4=SFA",
    }]))
    return results


def make_figures(results: pd.DataFrame) -> None:
    figure_dir = OUT / "figures"; figure_dir.mkdir(parents=True, exist_ok=True)
    primary = results[results.model == "random_forest"].copy()
    selected = primary[primary.experiment.str.contains("static_|adapt_")]
    if selected.empty:
        return
    labels = selected.dataset + "\n" + selected.experiment.str.replace("_20pct", "", regex=False)
    colors = ["#bf4040" if name.startswith("static") else "#2e8b57" for name in selected.experiment]
    plt.figure(figsize=(14, 7))
    plt.bar(range(len(selected)), selected.f1, color=colors)
    plt.xticks(range(len(selected)), labels, rotation=50, ha="right", fontsize=8)
    plt.ylim(0, 1.05); plt.ylabel("F1 score")
    plt.title("External RPL validation: static transfer versus limited adaptation")
    plt.tight_layout(); plt.savefig(figure_dir / "external_static_vs_adapted_f1.png", dpi=220); plt.close()


def own_comparison(results: pd.DataFrame) -> None:
    own_static = ROOT.parent / "Final Submission Evidence" / "02 Simulated Cooja Dataset and Construction Code" / "routing_features_v1" / "results" / "static_results.csv"
    own = pd.read_csv(own_static)
    own_row = own[(own.experiment == "static_blackhole_to_sinkhole") & (own.model == "cart") & (own.feature_set == "coarse_plus_routing")].iloc[0]
    external = results[(results.model == "random_forest") & results.experiment.str.contains("static_")]
    lines = [
        "# External RPL Dataset Validation — Comparison with Dissertation Cooja Work", "",
        "## What is directly comparable", "",
        "Both studies use held-out attack environments and evaluate static detection before limited target-attack adaptation.",
        "The metric names are comparable; raw fields, simulator, topology and split units are not.", "",
        "## Existing Cooja reference", "",
        f"The existing routing-aware CART test trained on Cooja Blackhole and tested on Cooja Sinkhole reported F1={own_row.f1:.4f}, recall={own_row.recall:.4f}, accuracy={own_row.accuracy:.4f}.",
        "This is the original within-platform concept-drift finding, not an external benchmark.", "",
        "## External static-transfer findings", "",
    ]
    for row in external.itertuples():
        lines.append(f"- {row.dataset}: {row.experiment} — F1={row.f1:.4f}, recall={row.recall:.4f}, accuracy={row.accuracy:.4f}.")
    lines += ["", "## Limited-target adaptation results", ""]
    static_to_adapt = [
        ("RADAR Blackhole → Sybil", "static_blackhole_to_sybil", "adapt_blackhole_to_sybil_20pct"),
        ("RADAR Sybil → Blackhole", "static_sybil_to_blackhole", "adapt_sybil_to_blackhole_20pct"),
        ("HUNSR Version → Decreased Rank", "static_version_to_decreased_rank", "adapt_version_to_decreased_rank_20pct"),
        ("HUNSR Version → DIS Flood", "static_version_to_dis_flood", "adapt_version_to_dis_flood_20pct"),
        ("HUNSR Version → Selective Forwarding", "static_version_to_selective_forwarding", "adapt_version_to_selective_forwarding_20pct"),
    ]
    for label, static_name, adapted_name in static_to_adapt:
        static = results[(results.model == "random_forest") & (results.experiment == static_name)].iloc[0]
        adapted = results[(results.model == "random_forest") & (results.experiment == adapted_name)].iloc[0]
        lines.append(f"- {label}: F1 {static.f1:.4f} → {adapted.f1:.4f}; recall {static.recall:.4f} → {adapted.recall:.4f} after 20% labelled target evidence.")
    lines += ["", "## Correct interpretation", "",
        "A low static-transfer F1 indicates distribution and/or mechanism shift. A higher adapted F1 shows that limited labelled target evidence can help in that external representation.",
        "These results do not establish a single model transferred from Cooja to NetSim: there is no defensible one-to-one raw feature schema. They are an external replication of the static-versus-adapted methodology.",
        "RADAR is NetSim packet traffic; UOS is Cooja packet traffic; HUNSR is Contiki-NG/Cooja-derived behavioural data. HUNSR temporal rows lack a published run identifier, so its temporal split is more conservative than random rows but is not equivalent to a whole-run split.",
    ]
    (OUT / "comparison_with_own_cooja_work.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True); DERIVED.mkdir(parents=True, exist_ok=True)
    radar = build_radar()
    uos = build_uos()
    results = radar_tests(radar) + uos_tests(uos) + hun_sr_tests()
    result_frame = pd.DataFrame(results).sort_values(["dataset", "experiment", "model"])
    write_csv(OUT / "external_validation_results.csv", result_frame)
    make_figures(result_frame)
    own_comparison(result_frame)
    audit = {
        "window_seconds": WINDOW_SECONDS,
        "radar_windows": len(radar),
        "uos_windows": len(uos),
        "models": ["random_forest"],
        "method": "Separate external replication. No external raw rows were merged into the dissertation Cooja dataset.",
    }
    (OUT / "run_audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(result_frame)} evaluation rows to {OUT}")


if __name__ == "__main__":
    main()

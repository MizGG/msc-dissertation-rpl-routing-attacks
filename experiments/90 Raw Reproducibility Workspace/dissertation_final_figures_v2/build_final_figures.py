#!/usr/bin/env python3
"""Generate final dissertation figures from completed, immutable result CSVs."""

from __future__ import annotations

import csv
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/dissertation_final_figures_v2"
FIGURES = OUT / "figures"
TABLES = OUT / "tables"
CROSS = ROOT / "experiments/cross_attack_drift_with_sybil_v1/results/cross_attack_matrix.csv"
ONLINE = ROOT / "experiments/online_drift_response_v1/results/detector_comparison_summary.csv"
ROBUST = ROOT / "experiments/robustness_campaign_v4/results/adaptation_summary.csv"
DEFENCE = ROOT / "experiments/sinkhole_defence_v1/results/defence_condition_summary.csv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], content: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(content)


def svg(path: Path, width: int, height: int, body: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    style = """
text { font-family: Arial, Helvetica, sans-serif; fill: #1f2933; }
.title { font-size: 21px; font-weight: 700; }
.subtitle { font-size: 12px; fill: #52616b; }
.label { font-size: 12px; }
.small { font-size: 10px; fill: #52616b; }
.axis { stroke: #9aa5b1; stroke-width: 1; }
.grid { stroke: #e4e7eb; stroke-width: 1; }
"""
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
        f'<rect width="100%" height="100%" fill="#ffffff"/>\n<style>{style}</style>\n'
        + "\n".join(body) + "\n</svg>\n",
        encoding="utf-8",
    )


def heat(value: float) -> str:
    # 0 is red, 1 is green, with light fill preserving labels.
    red = int(219 - 125 * value)
    green = int(77 + 110 * value)
    blue = int(72 + 35 * value)
    return f"rgb({red},{green},{blue})"


def cross_attack_heatmap(source: list[dict[str, str]]) -> list[dict[str, object]]:
    matrix = [row for row in source if row["evaluation"] == "cross_attack" and row["model"] == "cart"]
    families = sorted({row["train_family"] for row in matrix})
    values = {(row["train_family"], row["test_family"]): float(row["f1"]) for row in matrix}
    short = {
        "blackhole": "BH", "dio_suppression": "DIO-S", "dis_flood": "DIS-F",
        "grayhole": "GH", "increase_rank": "INC-R", "sinkhole": "SH",
        "sybil": "SYB", "wormhole": "WH", "worst_parent": "WP",
    }
    cell, x0, y0 = 61, 190, 138
    body = [
        '<text class="title" x="32" y="36">Cross-Attack IDS F1: Static CART</text>',
        '<text class="subtitle" x="32" y="59">Train on the row attack family; test on the column family. Explicit attack markers excluded.</text>',
        '<text class="small" x="32" y="81">Darker green indicates stronger F1; red indicates failure to transfer.</text>',
    ]
    for i, family in enumerate(families):
        x = x0 + i * cell + cell / 2
        body.append(f'<text class="small" text-anchor="middle" x="{x}" y="{y0 - 12}">{short[family]}</text>')
        y = y0 + i * cell + 37
        body.append(f'<text class="small" text-anchor="end" x="{x0 - 8}" y="{y}">{short[family]}</text>')
    result_rows = []
    for r, train in enumerate(families):
        for c, test in enumerate(families):
            x, y = x0 + c * cell, y0 + r * cell
            if train == test:
                body.append(f'<rect x="{x}" y="{y}" width="{cell - 2}" height="{cell - 2}" fill="#e4e7eb"/>')
                body.append(f'<text class="small" text-anchor="middle" x="{x + cell / 2}" y="{y + 36}">in-domain</text>')
                continue
            value = values[(train, test)]
            body.append(f'<rect x="{x}" y="{y}" width="{cell - 2}" height="{cell - 2}" fill="{heat(value)}"/>')
            body.append(f'<text class="label" text-anchor="middle" x="{x + cell / 2}" y="{y + 36}" fill="#ffffff">{value:.2f}</text>')
            result_rows.append({"train_family": train, "test_family": test, "static_cart_f1": round(value, 4)})
    body.extend([
        f'<text class="small" x="{x0}" y="{y0 + len(families) * cell + 25}">Rows: training family. Columns: held-out target family. Diagonal is omitted by design.</text>',
        f'<text class="small" x="{x0}" y="{y0 + len(families) * cell + 41}">Abbreviations: BH blackhole; DIO-S suppression; DIS-F flood; GH grayhole; INC-R increased rank; SH sinkhole; SYB Sybil; WH wormhole; WP worst-parent.</text>',
    ])
    svg(FIGURES / "cross_attack_cart_f1_heatmap.svg", 840, 770, body)
    return result_rows


def online_detection(source: list[dict[str, str]]) -> list[dict[str, object]]:
    body = [
        '<text class="title" x="32" y="38">Online Drift Detection After Sinkhole Activation</text>',
        '<text class="subtitle" x="32" y="60">Five held-out attack and five matched control runs. Attack activates at 240 seconds.</text>',
        '<line class="axis" x1="110" y1="300" x2="710" y2="300"/>',
        '<line class="axis" x1="110" y1="100" x2="110" y2="300"/>',
        '<text class="small" x="47" y="105">delay (s)</text>',
    ]
    max_delay = max(float(row["maximum_detection_delay_s"]) for row in source) or 1
    exported = []
    for idx, row in enumerate(source):
        delay = float(row["median_detection_delay_s"])
        x = 220 + idx * 230
        height = delay / max(60, max_delay) * 170
        body.append(f'<rect x="{x}" y="{300 - height}" width="100" height="{height}" fill="#2f80ed"/>')
        body.append(f'<text class="label" text-anchor="middle" x="{x + 50}" y="{290 - height}">{delay:.0f}s</text>')
        body.append(f'<text class="label" text-anchor="middle" x="{x + 50}" y="{330}">{escape(row["detector"])}</text>')
        body.append(f'<text class="small" text-anchor="middle" x="{x + 50}" y="{350}">{int(float(row["detected_without_prealarm"]))}/{int(float(row["attack_runs"]))} attacks</text>')
        body.append(f'<text class="small" text-anchor="middle" x="{x + 50}" y="{366}">{int(float(row["control_false_alarms"]))}/{int(float(row["control_runs"]))} controls false-alerted</text>')
        exported.append({
            "detector": row["detector"], "attack_detection_rate": row["attack_detection_rate"],
            "control_false_alarm_rate": row["control_false_alarm_rate"], "median_detection_delay_s": row["median_detection_delay_s"],
        })
    body.append('<text class="small" x="110" y="405">The zero-delay CUSUM signal occurred in the first 60-second post-activation window.</text>')
    svg(FIGURES / "online_drift_detection.svg", 820, 440, body)
    return exported


def robustness_adaptation(source: list[dict[str, str]]) -> list[dict[str, object]]:
    selected = [
        row for row in source
        if row["model"] == "cart" and row["feature_set"] == "coarse_plus_routing"
        and row["adaptation_seeds"] in {"0", "3"}
    ]
    selected.sort(key=lambda r: (r["condition"], r["family"], int(r["adaptation_seeds"])))
    groups = []
    for condition in ("ATTACKER_RELOCATED", "LOSSY_RADIO"):
        for family in ("blackhole", "sinkhole", "sybil"):
            groups.append([r for r in selected if r["condition"] == condition and r["family"] == family])
    x0, y0, bar_w, gap = 76, 355, 24, 82
    body = [
        '<text class="title" x="32" y="36">Robustness: Static vs Three-Seed Adapted F1</text>',
        '<text class="subtitle" x="32" y="59">CART with coarse plus routing features under attacker relocation and lossy radio conditions.</text>',
    ]
    for tick in (0, .25, .5, .75, 1):
        y = y0 - tick * 250
        body.append(f'<line class="grid" x1="{x0}" y1="{y}" x2="760" y2="{y}"/>')
        body.append(f'<text class="small" x="43" y="{y + 4}">{tick:.2f}</text>')
    body.append(f'<line class="axis" x1="{x0}" y1="{y0}" x2="760" y2="{y0}"/>')
    body.append(f'<line class="axis" x1="{x0}" y1="105" x2="{x0}" y2="{y0}"/>')
    exported = []
    for idx, group in enumerate(groups):
        static, adapted = sorted(group, key=lambda r: int(r["adaptation_seeds"]))
        x = x0 + 36 + idx * gap
        for offset, row, color in ((0, static, "#d64545"), (bar_w + 5, adapted, "#007d79")):
            f1 = float(row["mean_f1"])
            h = f1 * 250
            body.append(f'<rect x="{x + offset}" y="{y0 - h}" width="{bar_w}" height="{h}" fill="{color}"/>')
            body.append(f'<text class="small" text-anchor="middle" x="{x + offset + bar_w / 2}" y="{y0 - h - 7}">{f1:.2f}</text>')
        condition = "relocated" if static["condition"] == "ATTACKER_RELOCATED" else "lossy"
        body.append(f'<text class="small" text-anchor="middle" x="{x + 27}" y="{y0 + 20}">{static["family"]}</text>')
        body.append(f'<text class="small" text-anchor="middle" x="{x + 27}" y="{y0 + 34}">{condition}</text>')
        exported.extend({
            "condition": row["condition"], "family": row["family"], "adaptation_seeds": row["adaptation_seeds"],
            "mean_f1": row["mean_f1"], "mean_fpr": row["mean_fpr"],
        } for row in (static, adapted))
    body.extend([
        '<rect x="524" y="88" width="12" height="12" fill="#d64545"/><text class="small" x="542" y="99">static (zero target seeds)</text>',
        '<rect x="524" y="106" width="12" height="12" fill="#007d79"/><text class="small" x="542" y="117">adapted (three target seeds)</text>',
    ])
    svg(FIGURES / "robustness_static_vs_adapted_f1.svg", 820, 440, body)
    return exported


def defence_overhead(source: list[dict[str, str]]) -> list[dict[str, object]]:
    by_mode = {row["mode"]: row for row in source}
    control = by_mode["control"]
    metrics = [
        ("App responses", "mean_app_rx", "higher is better"),
        ("Radio transmissions", "mean_radio_tx", "lower is better"),
        ("Parent switches", "mean_parent_switches", "lower is better"),
    ]
    body = [
        '<text class="title" x="32" y="36">Sinkhole Defence Prototype: Operational Cost</text>',
        '<text class="subtitle" x="32" y="59">Five matched seeds; values are post-activation means. This is a negative mitigation result.</text>',
    ]
    exported = []
    for idx, (label, field, direction) in enumerate(metrics):
        values = [float(by_mode[mode][field]) for mode in ("control", "attack", "defence")]
        max_value = max(values) or 1
        x0, y0, width = 225, 110 + idx * 108, 450
        body.append(f'<text class="label" x="32" y="{y0 + 14}">{label}</text>')
        for bar_idx, (mode, value, color) in enumerate(zip(("control", "attack", "defence"), values, ("#7b8794", "#2f80ed", "#d64545"))):
            y = y0 + 26 + bar_idx * 22
            length = value / max_value * width
            body.append(f'<rect x="{x0}" y="{y}" width="{length}" height="15" fill="{color}"/>')
            body.append(f'<text class="small" x="{x0 + length + 7}" y="{y + 12}">{mode}: {value:.1f}</text>')
        exported.append({"metric": label, "interpretation": direction, "control": values[0], "attack": values[1], "defence": values[2]})
    body.append('<text class="small" x="32" y="425">The rank-parent intervention increased routing churn and radio activity while reducing application responses; it is not claimed as a successful defence.</text>')
    svg(FIGURES / "sinkhole_defence_operational_cost.svg", 820, 455, body)
    return exported


def main() -> None:
    cross = cross_attack_heatmap(rows(CROSS))
    online = online_detection(rows(ONLINE))
    robust = robustness_adaptation(rows(ROBUST))
    defence = defence_overhead(rows(DEFENCE))
    write_csv(TABLES / "cross_attack_cart_f1.csv", list(cross[0]), cross)
    write_csv(TABLES / "online_drift_detection_summary.csv", list(online[0]), online)
    write_csv(TABLES / "robustness_static_vs_adapted.csv", list(robust[0]), robust)
    write_csv(TABLES / "sinkhole_defence_operational_cost.csv", list(defence[0]), defence)
    print(f"Wrote final figures and source tables to {OUT}")


if __name__ == "__main__":
    main()

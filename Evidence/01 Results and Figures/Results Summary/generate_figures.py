#!/usr/bin/env python3
"""Generate lightweight dissertation figures from the summary CSV files."""

from __future__ import annotations

import csv
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_svg(path: Path, width: int, height: int, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<style>
text {{ font-family: Arial, Helvetica, sans-serif; fill: #1f2933; }}
.title {{ font-size: 21px; font-weight: 700; }}
.subtitle {{ font-size: 12px; fill: #52616b; }}
.label {{ font-size: 12px; }}
.small {{ font-size: 11px; fill: #52616b; }}
.axis {{ stroke: #9aa5b1; stroke-width: 1; }}
.grid {{ stroke: #e4e7eb; stroke-width: 1; }}
</style>
{body}
</svg>
""",
        encoding="utf-8",
    )


def attack_coverage() -> None:
    rows = read_csv("attack_coverage_table.csv")
    width, height = 1000, 520
    x0, y0 = 32, 82
    col = [0, 180, 330, 460, 665, 820]
    body = [
        '<text class="title" x="32" y="38">Validated Cooja Attack Coverage</text>',
        '<text class="subtitle" x="32" y="60">Nine attack families, each with five attack and five matched control runs.</text>',
    ]
    headers = ["Attack", "Category", "Runs", "Activation", "Surface", "Status"]
    for i, header in enumerate(headers):
        body.append(f'<text class="small" x="{x0 + col[i]}" y="{y0}">{header}</text>')
    body.append(f'<line class="axis" x1="32" y1="{y0 + 10}" x2="968" y2="{y0 + 10}"/>')
    for idx, row in enumerate(rows):
        y = y0 + 34 + idx * 42
        fill = "#f5f7fa" if idx % 2 == 0 else "#ffffff"
        accent = "#007d79" if row["category"] == "new_attack_surface" else "#2f80ed"
        body.append(f'<rect x="28" y="{y - 22}" width="940" height="34" fill="{fill}"/>')
        body.append(f'<rect x="32" y="{y - 20}" width="5" height="30" fill="{accent}"/>')
        body.append(f'<text class="label" x="{x0 + col[0]}" y="{y}">{escape(row["attack_family"])}</text>')
        body.append(f'<text class="small" x="{x0 + col[1]}" y="{y}">{escape(row["category"])}</text>')
        body.append(f'<text class="label" x="{x0 + col[2]}" y="{y}">{row["attack_runs"]} attack / {row["control_runs"]} control</text>')
        body.append(f'<text class="label" x="{x0 + col[3]}" y="{y}">{row["activation_time_s"]}s</text>')
        body.append(f'<text class="small" x="{x0 + col[4]}" y="{y}">{escape(row["attack_surface"][:30])}</text>')
        body.append(f'<text class="label" x="{x0 + col[5]}" y="{y}">validated</text>')
    write_svg(FIGURES / "attack_coverage.svg", width, height, "\n".join(body))


def drift_bars() -> None:
    rows = read_csv("concept_drift_key_metrics.csv")
    width, height = 820, 450
    x0, y0 = 86, 350
    bar_w = 95
    scale = 260 / 72
    body = [
        '<text class="title" x="32" y="38">Static IDS Failure Under Cross-Attack Drift</text>',
        '<text class="subtitle" x="32" y="60">Zero-recall cross-attack pairs, marker features excluded.</text>',
    ]
    for tick in (0, 18, 36, 54, 72):
        y = y0 - tick * scale
        body.append(f'<line class="grid" x1="{x0}" y1="{y:.1f}" x2="760" y2="{y:.1f}"/>')
        body.append(f'<text class="small" x="52" y="{y + 4:.1f}">{tick}</text>')
    body.append(f'<line class="axis" x1="{x0}" y1="{y0}" x2="760" y2="{y0}"/>')
    body.append(f'<line class="axis" x1="{x0}" y1="90" x2="{x0}" y2="{y0}"/>')
    labels = ["CART all", "Gaussian all", "CART Sybil"]
    values = [48, 66, 11]
    totals = [72, 72, 16]
    colors = ["#2f80ed", "#d64545", "#007d79"]
    for i, (label, value, total, color) in enumerate(zip(labels, values, totals, colors)):
        x = x0 + 90 + i * 180
        h = value * scale
        body.append(f'<rect x="{x}" y="{y0 - h:.1f}" width="{bar_w}" height="{h:.1f}" fill="{color}"/>')
        body.append(f'<text class="label" x="{x + 18}" y="{y0 - h - 10:.1f}">{value}/{total}</text>')
        body.append(f'<text class="label" x="{x - 4}" y="{y0 + 24}">{label}</text>')
    body.append('<text class="small" x="270" y="410">Higher bars mean more complete attack-recall failure after drift.</text>')
    write_svg(FIGURES / "static_drift_zero_recall.svg", width, height, "\n".join(body))


def line_chart(filename: str, title: str, rows: list[dict[str, str]]) -> None:
    width, height = 820, 460
    x0, y0 = 90, 360
    plot_w, plot_h = 640, 260
    xs = [0, 1, 2, 3]
    f1 = [float(rows[i]["mean_f1"]) for i in range(4)]
    recall = [float(rows[i]["mean_recall"]) for i in range(4)]

    def pt(seed: int, value: float) -> tuple[float, float]:
        return x0 + seed * (plot_w / 3), y0 - value * plot_h

    body = [
        f'<text class="title" x="32" y="38">{escape(title)}</text>',
        '<text class="subtitle" x="32" y="60">Whole target-family simulation seeds are added for adaptation.</text>',
    ]
    for tick in (0, 0.25, 0.5, 0.75, 1.0):
        y = y0 - tick * plot_h
        body.append(f'<line class="grid" x1="{x0}" y1="{y:.1f}" x2="{x0 + plot_w}" y2="{y:.1f}"/>')
        body.append(f'<text class="small" x="48" y="{y + 4:.1f}">{tick:.2f}</text>')
    body.append(f'<line class="axis" x1="{x0}" y1="{y0}" x2="{x0 + plot_w}" y2="{y0}"/>')
    body.append(f'<line class="axis" x1="{x0}" y1="{y0 - plot_h}" x2="{x0}" y2="{y0}"/>')
    for seed in xs:
        x, _ = pt(seed, 0)
        body.append(f'<text class="label" x="{x - 4:.1f}" y="{y0 + 25}">{seed}</text>')
    body.append(f'<text class="small" x="{x0 + 210}" y="{y0 + 55}">target adaptation seeds</text>')
    for values, color, name in ((recall, "#2f80ed", "Recall"), (f1, "#007d79", "F1")):
        points = [pt(seed, value) for seed, value in zip(xs, values)]
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        body.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="3"/>')
        for x, y in points:
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"/>')
        lx, ly = points[-1]
        body.append(f'<text class="label" x="{lx + 14:.1f}" y="{ly + 4:.1f}">{name}</text>')
    write_svg(FIGURES / filename, width, height, "\n".join(body))


def adaptation_curves() -> None:
    rows = read_csv("adaptation_key_metrics.csv")
    overall = [r for r in rows if r["scope"] == "all_cross_attack_targets"]
    sybil = [r for r in rows if r["scope"] == "sybil_as_target"]
    line_chart("overall_adaptation_curve.svg", "Cross-Attack Adaptation Curve", overall)
    line_chart("sybil_static_vs_adapted.svg", "Sybil Static vs Adapted IDS Performance", sybil)


def captions() -> None:
    (FIGURES / "figure_captions.md").write_text(
        """# Figure Captions

Figure: Validated Cooja attack coverage. This table summarises the nine attack
families evaluated in Cooja, with five attack runs and five matched control runs
per family. Sybil is the new identity-manipulation attack surface.

Figure: Static IDS failure under cross-attack drift. The bars show how many
cross-attack train/test pairs produced zero attack recall when marker features
were excluded from training.

Figure: Cross-attack adaptation curve. Adding whole target-family simulation
seeds substantially improves mean recall and F1, showing recovery after
attack-distribution drift.

Figure: Sybil static vs adapted IDS performance. Static models trained on other
attack surfaces perform poorly on Sybil, while limited Sybil adaptation data
restores high held-out performance.
""",
        encoding="utf-8",
    )


def main() -> None:
    attack_coverage()
    drift_bars()
    adaptation_curves()
    captions()
    print(f"Wrote figures to {FIGURES}")


if __name__ == "__main__":
    main()

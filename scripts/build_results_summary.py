#!/usr/bin/env python3
"""Build the consolidated dissertation result package from experiment CSVs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


MASTER_FIELDS = [
    "result_id",
    "dataset",
    "feature_resolution",
    "evaluation",
    "training_attack",
    "test_attack",
    "adaptation_sinkhole_seeds",
    "split_method",
    "splits",
    "train_units",
    "test_units",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "f2",
    "fpr",
    "tp",
    "tn",
    "fp",
    "fn",
    "interpretation",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required input: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find_row(rows: list[dict[str, str]], column: str, value: str) -> dict[str, str]:
    matches = [row for row in rows if row.get(column) == value]
    if len(matches) != 1:
        raise ValueError(f"Expected one row where {column}={value!r}; found {len(matches)}")
    return matches[0]


def find_adaptation(rows: list[dict[str, str]], seeds: int) -> dict[str, str]:
    return find_row(rows, "adaptation_sinkhole_seeds", str(seeds))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = fields or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def rounded(value: float) -> float:
    return round(value, 4)


def metrics_from_counts(tp: int, tn: int, fp: int, fn: int) -> dict[str, object]:
    total = tp + tn + fp + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    f2 = 5 * precision * recall / (4 * precision + recall) if 4 * precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {
        "test_units": total,
        "accuracy": rounded((tp + tn) / total) if total else 0.0,
        "precision": rounded(precision),
        "recall": rounded(recall),
        "f1": rounded(f1),
        "f2": rounded(f2),
        "fpr": rounded(fpr),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def aggregate(rows: list[dict[str, str]]) -> dict[str, object]:
    return metrics_from_counts(
        sum(int(row["tp"]) for row in rows),
        sum(int(row["tn"]) for row in rows),
        sum(int(row["fp"]) for row in rows),
        sum(int(row["fn"]) for row in rows),
    )


def direct_metrics(row: dict[str, str]) -> dict[str, object]:
    fields = ["test_units", "accuracy", "precision", "recall", "f1", "f2", "fpr", "tp", "tn", "fp", "fn"]
    result: dict[str, object] = {"test_units": int(row["n"])}
    for field in fields[1:7]:
        result[field] = float(row[field])
    for field in fields[7:]:
        result[field] = int(row[field])
    return result


def mean_metrics(row: dict[str, str]) -> dict[str, object]:
    return {
        "accuracy": float(row["mean_accuracy"]),
        "precision": float(row["mean_precision"]),
        "recall": float(row["mean_recall"]),
        "f1": float(row["mean_f1"]),
        "f2": float(row["mean_f2"]) if "mean_f2" in row else "",
        "fpr": float(row["mean_fpr"]) if "mean_fpr" in row else "",
        "tp": "",
        "tn": "",
        "fp": "",
        "fn": "",
    }


def result_row(**values: object) -> dict[str, object]:
    row = {field: "" for field in MASTER_FIELDS}
    row.update(values)
    return row


def parse_labels(value: str) -> dict[str, int]:
    parsed: dict[str, int] = {}
    for item in value.split(";"):
        if item:
            label, count = item.split(":", maxsplit=1)
            parsed[label] = int(count)
    return parsed


def build_master(inputs: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    run_results = inputs["run_results"]
    run_adaptation = inputs["run_adaptation"]
    window_results = inputs["window_results"]
    window_adaptation = inputs["window_adaptation"]
    gope_results = inputs["gope_results"]

    run_in_domain = aggregate([row for row in run_results if row["experiment"].startswith("blackhole_leave_seed_")])
    window_in_domain = aggregate(
        [row for row in window_results if row["experiment"].startswith("blackhole_window_leave_seed_")]
    )
    run_static = direct_metrics(find_row(run_results, "experiment", "concept_drift_train_blackhole_test_sinkhole"))
    window_static = direct_metrics(
        find_row(window_results, "experiment", "window_drift_train_blackhole_test_sinkhole")
    )
    run_adapted = mean_metrics(find_adaptation(run_adaptation, 3))
    window_adapted = mean_metrics(find_adaptation(window_adaptation, 3))
    gope_all_row = find_row(gope_results, "experiment", "gope_balanced_routing_features_all_labelled_attacks")
    gope_shift_row = find_row(gope_results, "experiment", "gope_train_blackhole_test_sinkhole")

    return [
        result_row(
            result_id="cooja_run_blackhole_in_domain",
            dataset="Cooja controlled dataset",
            feature_resolution="complete run",
            evaluation="in-domain validation",
            training_attack="blackhole",
            test_attack="blackhole",
            adaptation_sinkhole_seeds=0,
            split_method="leave-one-whole-seed-out; confusion counts aggregated",
            splits=5,
            train_units="8 runs per split",
            **run_in_domain,
            interpretation="Strong in-domain baseline on five held-out attack/control seed pairs.",
        ),
        result_row(
            result_id="cooja_run_blackhole_to_sinkhole_static",
            dataset="Cooja controlled dataset",
            feature_resolution="complete run",
            evaluation="static attack-distribution shift",
            training_attack="blackhole",
            test_attack="sinkhole",
            adaptation_sinkhole_seeds=0,
            split_method="train/test separated by attack family and complete run",
            splits=1,
            train_units="10 runs",
            **run_static,
            interpretation="All five sinkhole attacks were classified as normal; accuracy is chance-level on the balanced run set.",
        ),
        result_row(
            result_id="cooja_run_blackhole_to_sinkhole_adapt_3",
            dataset="Cooja controlled dataset",
            feature_resolution="complete run",
            evaluation="three-seed adaptation",
            training_attack="blackhole plus sinkhole adaptation runs",
            test_attack="held-out sinkhole",
            adaptation_sinkhole_seeds=3,
            split_method="mean over all 10 combinations of three adaptation seeds",
            splits=10,
            train_units="16 runs per split",
            test_units="4 held-out runs per split",
            **run_adapted,
            interpretation="Retraining did not recover attack detection because the coarse features do not expose rank manipulation.",
        ),
        result_row(
            result_id="cooja_window_blackhole_in_domain",
            dataset="Cooja controlled dataset",
            feature_resolution="60-second window",
            evaluation="in-domain validation",
            training_attack="blackhole",
            test_attack="blackhole",
            adaptation_sinkhole_seeds=0,
            split_method="leave-one-whole-seed-out; confusion counts aggregated",
            splits=5,
            train_units="72 windows per split",
            **window_in_domain,
            interpretation="Strong in-domain temporal baseline with one missed blackhole attack window.",
        ),
        result_row(
            result_id="cooja_window_blackhole_to_sinkhole_static",
            dataset="Cooja controlled dataset",
            feature_resolution="60-second window",
            evaluation="static attack-distribution shift",
            training_attack="blackhole",
            test_attack="sinkhole",
            adaptation_sinkhole_seeds=0,
            split_method="train/test separated by attack family and complete seed",
            splits=1,
            train_units="90 windows",
            **window_static,
            interpretation="Zero attack recall; 0.7222 accuracy is the all-normal majority baseline (65 of 90 windows).",
        ),
        result_row(
            result_id="cooja_window_blackhole_to_sinkhole_adapt_3",
            dataset="Cooja controlled dataset",
            feature_resolution="60-second window",
            evaluation="three-seed adaptation",
            training_attack="blackhole plus sinkhole adaptation windows",
            test_attack="held-out sinkhole",
            adaptation_sinkhole_seeds=3,
            split_method="mean over all 10 combinations of three adaptation seeds",
            splits=10,
            train_units="144 windows per split",
            test_units="36 held-out windows per split",
            **window_adapted,
            interpretation="Recall recovered to 1.0, but FPR rose to 0.70; this is an over-alerting trade-off, not clean recovery.",
        ),
        result_row(
            result_id="gope_all_labelled_preliminary",
            dataset="Supplied Gope dataset",
            feature_resolution="row",
            evaluation="preliminary multi-attack baseline",
            training_attack="seven labelled attack files",
            test_attack="seven labelled attack files",
            adaptation_sinkhole_seeds="not applicable",
            split_method="class-balanced per attack; stratified random row holdout",
            splits=1,
            train_units=f"{gope_all_row['train_rows']} rows",
            **direct_metrics(gope_all_row),
            interpretation="Routing-aware Gaussian baseline has high precision but low recall; row leakage remains a validity limitation.",
        ),
        result_row(
            result_id="gope_blackhole_to_sinkhole_static",
            dataset="Supplied Gope dataset",
            feature_resolution="row",
            evaluation="static attack-distribution shift",
            training_attack="blackhole",
            test_attack="sinkhole",
            adaptation_sinkhole_seeds=0,
            split_method="train/test separated by attack file; class-balanced samples",
            splits=1,
            train_units=f"{gope_shift_row['train_rows']} rows",
            **direct_metrics(gope_shift_row),
            interpretation="Weak cross-attack transfer also appears in the external supplied data: recall is 0.0472.",
        ),
    ]


def build_static_figure(master: list[dict[str, object]]) -> list[dict[str, object]]:
    wanted = {
        "cooja_run_blackhole_to_sinkhole_static",
        "cooja_run_blackhole_to_sinkhole_adapt_3",
        "cooja_window_blackhole_to_sinkhole_static",
        "cooja_window_blackhole_to_sinkhole_adapt_3",
        "gope_blackhole_to_sinkhole_static",
    }
    return [
        {
            "result_id": row["result_id"],
            "dataset": row["dataset"],
            "feature_resolution": row["feature_resolution"],
            "adaptation_sinkhole_seeds": row["adaptation_sinkhole_seeds"],
            "accuracy": row["accuracy"],
            "precision": row["precision"],
            "recall": row["recall"],
            "f1": row["f1"],
            "f2": row["f2"],
            "fpr": row["fpr"],
        }
        for row in master
        if row["result_id"] in wanted
    ]


def build_adaptation_figure(inputs: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for resolution, source in (
        ("complete run", inputs["run_adaptation"]),
        ("60-second window", inputs["window_adaptation"]),
    ):
        for row in source:
            rows.append({
                "feature_resolution": resolution,
                "adaptation_sinkhole_seeds": int(row["adaptation_sinkhole_seeds"]),
                "splits": int(row["splits"]),
                "mean_accuracy": float(row["mean_accuracy"]),
                "mean_precision": float(row["mean_precision"]),
                "mean_recall": float(row["mean_recall"]),
                "mean_f1": float(row["mean_f1"]),
                "mean_f2": float(row["mean_f2"]) if "mean_f2" in row else "",
                "mean_fpr": float(row["mean_fpr"]) if "mean_fpr" in row else "",
            })
    return rows


def build_gope_counts(audit: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in audit:
        labels = parse_labels(row["label_counts"])
        rows.append({
            "attack": row["attack"],
            "rows": int(row["rows"]),
            "columns": int(row["columns"]),
            "has_TYPE_label": int(row["has_TYPE_label"]),
            "normal_rows": labels.get("Normal", ""),
            "attack_rows": labels.get("Attack", ""),
        })
    if sum(int(row["rows"]) for row in rows) != 768811:
        raise ValueError("Gope dataset row total no longer matches the audited 768,811 rows")
    return rows


def feature_gap_rows() -> list[dict[str, object]]:
    return [
        {"feature_family": "application delivery", "current_cooja_evidence": "UDP request/response and missed-response counts", "gope_routing_feature": "pkt_loss; cpkt_loss", "coverage": "indirect", "sinkhole_relevance": "Low: delivery volume changed little between sinkhole attack and control."},
        {"feature_family": "radio activity", "current_cooja_evidence": "transmission, byte and sender counts", "gope_routing_feature": "RSSI(dbm); TX_RX_Distance", "coverage": "partial", "sinkhole_relevance": "Low alone: sinkhole attack/control radio totals were nearly identical."},
        {"feature_family": "rank state", "current_cooja_evidence": "explicit attack marker retained only for validation and excluded from training", "gope_routing_feature": "Source_Rank", "coverage": "missing non-leaking feature", "sinkhole_relevance": "Critical: the implemented sinkhole manipulates advertised RPL rank."},
        {"feature_family": "parent state", "current_cooja_evidence": "parent-found and no-parent event counts", "gope_routing_feature": "Parrent_Node; Parents_Count; same_parent", "coverage": "partial", "sinkhole_relevance": "High: an attractive rank can change preferred-parent selection."},
        {"feature_family": "RPL control traffic", "current_cooja_evidence": "not separated by DIO, DAO and DIS message type", "gope_routing_feature": "Src_DIO_count; Dst_DIO_count; Src_DAO_count; Dst_DAO_count; Src_DIS_count; Dst_DIS_count", "coverage": "missing", "sinkhole_relevance": "High: exposes routing-control changes without using attack log text."},
        {"feature_family": "route length", "current_cooja_evidence": "not extracted", "gope_routing_feature": "hop_count; Avg_hop_count", "coverage": "missing", "sinkhole_relevance": "High: parent attraction can alter path length and route structure."},
    ]


def render_interpretation(
    master: list[dict[str, object]], diagnostics: list[dict[str, str]]
) -> str:
    by_id = {str(row["result_id"]): row for row in master}
    diagnostic_map = {(row["family"], row["feature"]): row for row in diagnostics}
    blackhole_responses = abs(float(diagnostic_map[("blackhole", "app_received_responses")]["difference"]))
    blackhole_radio = abs(float(diagnostic_map[("blackhole", "radio_transmissions")]["difference"]))
    sinkhole_responses = abs(float(diagnostic_map[("sinkhole", "app_received_responses")]["difference"]))
    sinkhole_radio = abs(float(diagnostic_map[("sinkhole", "radio_transmissions")]["difference"]))
    window_in_domain = by_id["cooja_window_blackhole_in_domain"]
    window_static = by_id["cooja_window_blackhole_to_sinkhole_static"]
    window_adapted = by_id["cooja_window_blackhole_to_sinkhole_adapt_3"]
    gope_shift = by_id["gope_blackhole_to_sinkhole_static"]
    return f"""# Consolidated Concept-Drift Results

## Research Claim Supported by the Current Evidence

The experiments support a bounded claim: an IDS trained on blackhole behaviour does not reliably generalise when the malicious mechanism changes to sinkhole rank manipulation. This is a controlled attack-distribution shift used to evaluate concept drift; it is not evidence that every natural 6LoWPAN deployment will drift in the same way.

## Main Findings

1. **The baseline works before the attack change.** Whole-seed blackhole validation achieved perfect run-level detection. The 60-second model produced aggregate accuracy {float(window_in_domain['accuracy']):.4f}, recall {float(window_in_domain['recall']):.4f} and F1 {float(window_in_domain['f1']):.4f} across the five held-out blackhole seeds. This establishes that the pipeline can learn a stable in-domain attack signal.
2. **Static transfer fails after the attack mechanism changes.** The run-level blackhole model classified all five sinkhole attacks as normal, giving recall and F1 of 0. At window level, recall and F1 also remained 0. The apparent accuracy of {float(window_static['accuracy']):.4f} is only the majority-class baseline: 65 of 90 sinkhole evaluation windows are normal, and the model predicted every window as normal.
3. **Simple adaptation is representation-limited.** Adding one, two or three complete sinkhole seeds did not improve the run-level model. At window level, three adaptation seeds raised mean recall to {float(window_adapted['recall']):.4f} and mean F1 to {float(window_adapted['f1']):.4f}, but mean false-positive rate rose to {float(window_adapted['fpr']):.4f}. The detector recovered sensitivity by over-alerting, so this cannot be described as successful adaptation without qualification.
4. **The supplied Gope data independently supports the transfer problem.** A preliminary routing-aware Gaussian model trained on Gope blackhole rows achieved only {float(gope_shift['recall']):.4f} recall and {float(gope_shift['f1']):.4f} F1 on Gope sinkhole rows. This is corroborating evidence, not a direct replication, because the supplied files expose no run identifiers and the current split is row-based.

## Mechanistic Interpretation

The negative result is explainable. Blackhole runs produce a large throughput and radio-volume change because forwarded traffic is dropped. In the extracted run-level features, mean received responses fall by {blackhole_responses:.1f} and mean radio transmissions by {blackhole_radio:.1f} relative to matched controls. Sinkhole attack and control runs differ by only {sinkhole_responses:.1f} received responses and {sinkhole_radio:.1f} radio transmissions on average. The current Cooja representation therefore captures the blackhole consequence but not the sinkhole mechanism.

The Gope audit shows what is missing: rank, parent identity and count, typed DIO/DAO/DIS counters, hop count and packet loss. These are routing-state features with a defensible causal relationship to sinkhole behaviour. The next model milestone should instrument those signals in Cooja and then repeat exactly the same whole-seed static and adaptation evaluation.

## Validity Boundaries

- The Cooja dataset has five matched seeds per attack/control condition. This is adequate for a controlled proof of concept but too small for broad deployment claims.
- Adaptation and evaluation are separated by complete Cooja seed, preventing windows or runs from the same simulation entering both sets.
- Explicit blackhole and sinkhole log markers are excluded from model inputs; they are retained only to validate attack activation.
- The Gope baseline is preliminary because the source files lack run identifiers. Random row holdout may inflate in-domain performance, so it must not be presented as a final paper reproduction.
- Mean adaptation scores average overlapping combinations of held-out seeds. They describe sensitivity across the available seeds, not independent repeated trials.

## Defensible Dissertation Conclusion So Far

The strongest conclusion is not that retraining automatically solves drift. It is that adaptation depends on representation: when the feature space omits the changed attack mechanism, a static detector fails and naive retraining either remains ineffective or recovers recall at an unacceptable false-positive cost. That is a useful Master's-level finding because it links the observed model failure to RPL attack mechanics and produces a concrete, testable next step.
"""


def metric_table_row(label: str, row: dict[str, object]) -> str:
    values = " | ".join(f"{float(row[field]):.4f}" for field in ("accuracy", "precision", "recall", "f1", "f2", "fpr"))
    return f"| {label} | {values} |"


def render_results_section(master: list[dict[str, object]]) -> str:
    rows = {str(row["result_id"]): row for row in master}
    table = "\n".join([
        metric_table_row("Cooja run, blackhole in-domain", rows["cooja_run_blackhole_in_domain"]),
        metric_table_row("Cooja run, static blackhole to sinkhole", rows["cooja_run_blackhole_to_sinkhole_static"]),
        metric_table_row("Cooja window, blackhole in-domain", rows["cooja_window_blackhole_in_domain"]),
        metric_table_row("Cooja window, static blackhole to sinkhole", rows["cooja_window_blackhole_to_sinkhole_static"]),
        metric_table_row("Cooja window, three-seed adaptation (mean)", rows["cooja_window_blackhole_to_sinkhole_adapt_3"]),
        metric_table_row("Gope rows, static blackhole to sinkhole", rows["gope_blackhole_to_sinkhole_static"]),
    ])
    return f"""# Dissertation Results So Far

## Controlled Attack-Distribution Shift

The IDS was first evaluated under stable blackhole conditions and then under a controlled change from blackhole packet dropping to sinkhole rank manipulation. All Cooja train/test partitions were separated by complete simulation seed. Attack markers used to verify activation were excluded from classifier features.

| Dataset and evaluation | Accuracy | Precision | Recall | F1 | F2 | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{table}

The strong blackhole results demonstrate that the experimental pipeline can learn a stable in-domain signal. When the frozen detector was transferred to sinkhole data, attack recall fell to zero at both run and window resolutions. Window accuracy remained 0.7222 only because 65 of the 90 evaluation windows were labelled normal; the confusion matrix was TN=65, FN=25, TP=0 and FP=0. Accuracy is therefore not evidence of detection in this condition.

## Adaptation

Adaptation data were added by complete sinkhole seed, and testing used only unseen seeds. One or two sinkhole seeds produced no window-level detection. With three adaptation seeds, mean recall increased to 1.0000 and mean F1 to 0.5237, but mean FPR increased to 0.7000 and precision remained 0.3547. The adapted model therefore detected attack windows by labelling many normal windows as malicious. Run-level adaptation remained at zero recall for every tested adaptation size.

This result rejects the simplistic assumption that retraining alone resolves concept drift. The feature representation must expose the changed mechanism. Current application and radio-volume summaries show a pronounced blackhole effect but almost no sinkhole attack/control separation. Sinkhole detection requires routing-aware evidence such as advertised rank, preferred-parent changes, parent count, typed RPL control-message counts and hop-count changes.

## External Dataset Check

The supplied Gope collection contains 768,811 rows across eight attack files. Seven files include a supervised `TYPE` label and routing-aware fields; Worst Parent has no `TYPE` label and is excluded from the preliminary supervised baseline. A routing-aware Gaussian model trained on balanced blackhole rows and tested on balanced sinkhole rows achieved accuracy 0.5083, recall 0.0472 and F1 0.0876. The weak transfer is consistent with the Cooja finding, although the result is preliminary because the supplied CSVs do not provide simulation-run identifiers.

## Result Position

Taken together, the evidence shows a reproducible attack-distribution shift, static-model failure, and a measurable but operationally poor adaptation response. The immediate scientific task is to add non-leaking RPL routing-state features to the Cooja logs and rerun the same seed-separated protocol. Only after that feature milestone should a formal drift detector and LLM explanation layer be evaluated.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments-dir", type=Path, default=Path("experiments"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/results"))
    args = parser.parse_args()

    inputs = {
        "run_results": read_csv(args.experiments_dir / "ml_baseline/baseline_results.csv"),
        "run_adaptation": read_csv(args.experiments_dir / "ml_baseline/adaptation_summary.csv"),
        "window_results": read_csv(args.experiments_dir / "ml_window/window_results.csv"),
        "window_adaptation": read_csv(args.experiments_dir / "ml_window/window_adaptation_summary.csv"),
        "gope_audit": read_csv(args.experiments_dir / "gope_dataset/audit_summary.csv"),
        "gope_results": read_csv(args.experiments_dir / "gope_dataset/gope_baseline_results.csv"),
        "feature_diagnostics": read_csv(args.experiments_dir / "ml_baseline/feature_diagnostics.csv"),
    }

    master = build_master(inputs)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "master_results_summary.csv", master, MASTER_FIELDS)
    write_csv(args.out_dir / "static_vs_adapted_figure.csv", build_static_figure(master))
    write_csv(args.out_dir / "adaptation_curve_figure.csv", build_adaptation_figure(inputs))
    write_csv(args.out_dir / "gope_dataset_row_counts.csv", build_gope_counts(inputs["gope_audit"]))
    write_csv(args.out_dir / "feature_gap_summary.csv", feature_gap_rows())
    (args.out_dir / "results_interpretation.md").write_text(
        render_interpretation(master, inputs["feature_diagnostics"]), encoding="utf-8"
    )
    (args.out_dir / "DISSERTATION_RESULTS_SO_FAR.md").write_text(render_results_section(master), encoding="utf-8")
    (args.out_dir / "README.md").write_text(
        "# Consolidated Results Package\n\n"
        "Run `python3 scripts/build_results_summary.py` from the repository root to regenerate this directory.\n\n"
        "The CSV files are figure-ready source tables. The Markdown files contain a concise interpretation and a dissertation-ready results section. All values are derived from the preserved Cooja and supplied-Gope experiment outputs; no attack-marker field is used as a model feature.\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(master)} consolidated results to {args.out_dir}")


if __name__ == "__main__":
    main()

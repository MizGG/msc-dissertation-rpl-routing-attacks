#!/usr/bin/env python3
"""A stricter second external experiment: balanced incremental adaptation.

Protocol: source-attack traces/time are used for source training; different,
labelled target-attack traces/time supply 0--100% adaptation evidence; a fixed
set of target traces/time and normal traffic remains untouched until final test.
The output is an adaptation curve, not a cherry-picked single split.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "derived_data"
OUT = ROOT / "results" / "balanced_incremental_adaptation"
FRACTIONS = (0.0, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 1.0)


def balance_train(data: pd.DataFrame) -> pd.DataFrame:
    attack = data[data.label == 1]
    normal = data[data.label == 0]
    if attack.empty or normal.empty:
        raise ValueError("Both classes required")
    return pd.concat([attack, normal.sample(n=len(attack), random_state=42)]).sample(frac=1, random_state=42)


def evaluate(dataset: str, direction: str, fraction: float, train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> dict[str, object]:
    balanced = balance_train(train)
    usable_features = [feature for feature in features if balanced[feature].nunique(dropna=False) > 1]
    if not usable_features:
        raise ValueError("No non-constant training features")
    model = Pipeline([
        ("select", SelectKBest(f_classif, k=min(10, len(usable_features)))),
        ("model", ExtraTreesClassifier(
            n_estimators=350, max_depth=10, min_samples_leaf=2,
            class_weight="balanced", random_state=42, n_jobs=-1,
        )),
    ])
    model.fit(balanced[usable_features], balanced.label)
    prediction = model.predict(test[usable_features])
    return {
        "dataset": dataset, "direction": direction, "target_evidence_fraction": fraction,
        "model": "balanced_extra_trees_selectkbest", "features_offered": len(features),
        "features_selected": ";".join(usable_features[index] for index in model.named_steps["select"].get_support(indices=True)),
        "train_rows_before_balance": len(train), "train_rows_after_balance": len(balanced),
        "test_rows": len(test), "attack_test_rows": int(test.label.sum()),
        "accuracy": round(float(accuracy_score(test.label, prediction)), 4),
        "precision": round(float(precision_score(test.label, prediction, zero_division=0)), 4),
        "recall": round(float(recall_score(test.label, prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(test.label, prediction, zero_division=0)), 4),
    }


def radar_curve(data: pd.DataFrame, source_family: str, target_family: str) -> list[dict[str, object]]:
    features = [c for c in data.columns if c not in {"group", "window", "label", "family"}]
    normal = data[data.family == "legitimate"]
    normal_train = normal[~normal.group.isin({"legitimate_111", "legitimate_112", "legitimate_113", "legitimate_114", "legitimate_115"})]
    normal_test = normal[normal.group.isin({"legitimate_111", "legitimate_112", "legitimate_113", "legitimate_114", "legitimate_115"})]
    source = data[data.family == source_family]
    target = data[data.family == target_family]
    source_train = source[~source.group.isin({f"{source_family}_104", f"{source_family}_105"})]
    target_adapt = target[~target.group.isin({f"{target_family}_104", f"{target_family}_105"})]
    target_test = target[target.group.isin({f"{target_family}_104", f"{target_family}_105"})]
    test = pd.concat([normal_test, target_test])
    results = []
    for fraction in FRACTIONS:
        take = target_adapt.sample(frac=fraction, random_state=42) if fraction else target_adapt.iloc[:0]
        train = pd.concat([normal_train, source_train, take])
        results.append(evaluate("RADAR", f"{source_family}_to_{target_family}", fraction, train, test, features))
    return results


def hunsr_curves() -> list[dict[str, object]]:
    raw = pd.read_csv(ROOT / "HUNSR_RPL_IDS_Behavior" / "RPL-IDS-Beh.csv").rename(columns={"label": "source_label"})
    raw["label"] = (raw.source_label != 0).astype(int)
    features = [c for c in raw.columns if c not in {"time_sec", "node_id", "parent_id", "source_label", "label"}]
    raw = raw.sort_values(["time_sec", "node_id"]).reset_index(drop=True)
    early, late = raw.iloc[:int(0.70 * len(raw))], raw.iloc[int(0.70 * len(raw)):]
    normal_early, normal_late = early[early.source_label == 0], late[late.source_label == 0]
    source = early[early.source_label == 1]  # Version Number Attack
    targets = {2: "decreased_rank", 3: "dis_flood", 4: "selective_forwarding"}
    results = []
    for label, name in targets.items():
        target_adapt = early[early.source_label == label]
        target_test = late[late.source_label == label]
        test = pd.concat([normal_late, target_test])
        for fraction in FRACTIONS:
            take = target_adapt.sample(frac=fraction, random_state=42) if fraction else target_adapt.iloc[:0]
            train = pd.concat([normal_early, source, take])
            results.append(evaluate("HUNSR", f"version_to_{name}", fraction, train, test, features))
    return results


def make_figure(results: pd.DataFrame) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(11, 6))
    for (dataset, direction), group in results.groupby(["dataset", "direction"]):
        group = group.sort_values("target_evidence_fraction")
        plt.plot(group.target_evidence_fraction * 100, group.f1, marker="o", label=f"{dataset}: {direction}")
    plt.xlabel("Labelled target-attack evidence used for adaptation (%)")
    plt.ylabel("Held-out target F1")
    plt.ylim(0, 1.05); plt.grid(alpha=0.25); plt.legend(fontsize=8)
    plt.title("Balanced incremental adaptation on external RPL data")
    plt.tight_layout(); plt.savefig(OUT / "balanced_incremental_adaptation_curve.png", dpi=220); plt.close()


def main() -> None:
    radar = pd.read_csv(DERIVED / "radar_60s_windows.csv")
    results = radar_curve(radar, "blackhole", "sybil") + radar_curve(radar, "sybil", "blackhole") + hunsr_curves()
    frame = pd.DataFrame(results).sort_values(["dataset", "direction", "target_evidence_fraction"])
    OUT.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT / "balanced_incremental_adaptation_results.csv", index=False)
    make_figure(frame)
    best = frame.loc[frame.groupby(["dataset", "direction"])["f1"].idxmax()].sort_values(["dataset", "direction"])
    best.to_csv(OUT / "best_held_out_f1_by_direction.csv", index=False)
    print(f"Wrote {len(frame)} curve rows to {OUT}")


if __name__ == "__main__":
    main()

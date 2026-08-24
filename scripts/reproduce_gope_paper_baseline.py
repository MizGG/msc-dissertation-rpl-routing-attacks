
"""Reproduce static six-feature baselines on the supplied Gope attack files.

This preserves the earlier reproduction approach: per-attack 70/30 random and
source-order splits, training-only Random Forest top-six feature selection, and
Decision Tree/Random Forest evaluation. It is intentionally not described as a
reproduction of the paper's full adversarial RL and online adaptation system.
"""

import argparse
from pathlib import Path
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_score, recall_score, fbeta_score, f1_score, accuracy_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.impute import SimpleImputer

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dataset-dir",
    type=Path,
    default=Path("/Users/mizzy/Documents/Dissertation/Dissertation_Cooja_Work/DR P"),
)
parser.add_argument(
    "--out-dir",
    type=Path,
    default=Path("experiments/gope_dataset/paper_baseline_reproduction"),
)
args = parser.parse_args()
OUT = args.out_dir
OUT.mkdir(parents=True, exist_ok=True)
csvs = sorted(path for path in args.dataset_dir.rglob("*.csv") if "__MACOSX" not in path.parts)
if len(csvs) != 8:
    raise SystemExit(f"Expected eight supplied attack CSVs, found {len(csvs)} in {args.dataset_dir}")

base_candidates = [
    "PKT_TYPE", "CONTROL_PACKET_TYPE/APP_NAME", "PKT_STATUS", "PACKET_STATUS",
    "APP_LAYER_PAYLOAD(Bytes)", "TRX_LAYER_PAYLOAD(Bytes)", "NW_LAYER_PAYLOAD(Bytes)",
    "MAC_LAYER_PAYLOAD(Bytes)", "PHY_LAYER_PAYLOAD(Bytes)", "PHY_LAYER_OVERHEAD(Bytes)",
    "RSSI(dbm)", "TX_RX_Distance", "NEIGHBOUR_COUNT", "RPL_NEIGHBOUR_COUNT",
    "Source_Rank", "Parrent_Node", "Number_of_Sibils", "Parents_Count", "LQ_SN_PN",
    "Sibiling_Same_Parent", "CMP_LQ_PP_OP", "Dst_DAO_count", "Src_DAO_count",
    "Src_DAOAck_count", "Trs_DAOAck_count", "Dst_DAOAck_count", "Src_host_count",
    "Rcv_host_count", "Dst_host_count", "RANK_ALT_COUNT", "Src_DIS_count",
    "Dst_DIS_count", "Src_DIO_count", "src_cpkt_count", "dst_cpkt_count",
    "Dst_DIO_count", "CHILD_COUNT", "hop_count", "same_parent", "Avg_hop_count",
    "PRT_BST_LQ", "PKT_E2E_DELAY", "pkt_loss", "cpkt_loss", "Trp_app_count"
]

def infer_attack_name(folder):
    import re
    m = re.search(r"\((.*?)\)", folder)
    code = m.group(1) if m else folder
    full = folder.split("(")[0].strip()
    return code, full

def prepare_df(path, max_per_class=30000, seed=42):
    allcols = pd.read_csv(path, nrows=0).columns.tolist()
    usecols = [c for c in base_candidates if c in allcols]
    target_col = "TYPE" if "TYPE" in allcols else "Node_Type"
    df = pd.read_csv(path, usecols=usecols + [target_col], low_memory=False)
    if target_col == "TYPE":
        df = df[df[target_col].isin(["Normal", "Attack"])].copy()
        y = (df[target_col] == "Attack").astype(int)
    else:
        df = df[df[target_col].isin([0, 1, 0.0, 1.0])].copy()
        y = (df[target_col].astype(float) == 1.0).astype(int)

    X = df.drop(columns=[target_col]).dropna(axis=1, how="all")
    data = X.copy()
    data["__y__"] = y.values

    parts = []
    for label, grp in data.groupby("__y__"):
        if len(grp) > max_per_class:
            parts.append(grp.sample(max_per_class, random_state=seed))
        else:
            parts.append(grp)

    data = pd.concat(parts).sample(frac=1, random_state=seed).reset_index(drop=True)
    y = data.pop("__y__").astype(int).values
    return data, y, target_col

def prepare_df_ordered(path, max_rows=120000):
    allcols = pd.read_csv(path, nrows=0).columns.tolist()
    usecols = [c for c in base_candidates if c in allcols]
    target_col = "TYPE" if "TYPE" in allcols else "Node_Type"
    df = pd.read_csv(path, usecols=usecols + [target_col], low_memory=False)
    if target_col == "TYPE":
        df = df[df[target_col].isin(["Normal", "Attack"])].copy()
        y = (df[target_col] == "Attack").astype(int).values
    else:
        df = df[df[target_col].isin([0, 1, 0.0, 1.0])].copy()
        y = (df[target_col].astype(float) == 1.0).astype(int).values

    X = df.drop(columns=[target_col]).dropna(axis=1, how="all")
    if len(X) > max_rows:
        idx = np.linspace(0, len(X) - 1, max_rows).astype(int)
        X = X.iloc[idx].reset_index(drop=True)
        y = y[idx]
    return X, y, target_col

def make_preprocessor(X, selected_cols=None):
    if selected_cols is None:
        selected_cols = X.columns.tolist()
    Xs = X[selected_cols]
    cat_cols = [c for c in selected_cols if Xs[c].dtype == "object"]
    num_cols = [c for c in selected_cols if c not in cat_cols]
    return ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), num_cols),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ]), cat_cols)
    ], remainder="drop", verbose_feature_names_out=False)

def metrics(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "accuracy": accuracy_score(y_true, y_pred) * 100,
        "precision": precision_score(y_true, y_pred, zero_division=0) * 100,
        "recall": recall_score(y_true, y_pred, zero_division=0) * 100,
        "f1": f1_score(y_true, y_pred, zero_division=0) * 100,
        "f2": fbeta_score(y_true, y_pred, beta=2, zero_division=0) * 100,
        "fpr": fp / (fp + tn) if (fp + tn) > 0 else 0,
        "tn": tn, "fp": fp, "fn": fn, "tp": tp
    }

def select_top6(X_train, y_train):
    pre = make_preprocessor(X_train)
    Xt = pre.fit_transform(X_train)
    names = pre.get_feature_names_out()
    rf = RandomForestClassifier(
        n_estimators=80, max_depth=12, random_state=42,
        n_jobs=-1, class_weight="balanced_subsample"
    )
    rf.fit(Xt, y_train)
    imp = {}
    for nm, val in zip(names, rf.feature_importances_):
        orig = None
        for c in X_train.columns:
            if nm == c or nm.startswith(c + "_"):
                orig = c
                break
        if orig is None:
            orig = nm
        imp[orig] = imp.get(orig, 0) + val
    return [k for k, v in sorted(imp.items(), key=lambda kv: kv[1], reverse=True)[:6]], imp

results = []
selected_rows = []

for path in csvs:
    folder = path.parent.name
    code, attack = infer_attack_name(folder)
    X, y, target_col = prepare_df(path)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    top6, imp = select_top6(X_train, y_train)
    for rank, f in enumerate(top6, 1):
        selected_rows.append({"attack_code": code, "attack": attack, "rank": rank, "feature": f, "importance": imp[f]})

    models = {
        "KNN_top6": KNeighborsClassifier(n_neighbors=5),
        "DecisionTree_top6": DecisionTreeClassifier(max_depth=12, random_state=42, class_weight="balanced"),
        "RandomForest_top6": RandomForestClassifier(n_estimators=120, max_depth=14, random_state=42, n_jobs=-1, class_weight="balanced_subsample"),
        "RandomForest_all_features": RandomForestClassifier(n_estimators=120, max_depth=14, random_state=42, n_jobs=-1, class_weight="balanced_subsample")
    }

    for name, model in models.items():
        cols = top6 if "top6" in name else X_train.columns.tolist()
        pipe = Pipeline([("pre", make_preprocessor(X_train, cols)), ("model", model)])
        pipe.fit(X_train[cols], y_train)
        pred = pipe.predict(X_test[cols])
        results.append({
            "attack_code": code, "attack": attack, "folder": folder,
            "target_col": target_col, "split": "random_stratified_70_30",
            "rows_used": len(X), "normal_used": int((y == 0).sum()),
            "attack_used": int((y == 1).sum()), "model": name,
            "num_features": len(cols), **metrics(y_test, pred)
        })

pd.DataFrame(results).to_csv(OUT / "actual_dataset_random_split_results.csv", index=False)
pd.DataFrame(selected_rows).to_csv(OUT / "selected_top6_features_random_split.csv", index=False)

temporal_results = []
temporal_selected = []

for path in csvs:
    folder = path.parent.name
    code, attack = infer_attack_name(folder)
    X, y, target_col = prepare_df_ordered(path)
    split = int(0.7 * len(X))
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y[:split], y[split:]

    if len(np.unique(y_train)) < 2 or len(np.unique(y_test)) < 2:
        continue

    top6, imp = select_top6(X_train, y_train)
    for rank, f in enumerate(top6, 1):
        temporal_selected.append({"attack_code": code, "attack": attack, "rank": rank, "feature": f, "importance": imp[f]})

    for name, model in {
        "DecisionTree_top6_temporal": DecisionTreeClassifier(max_depth=12, random_state=42, class_weight="balanced"),
        "RandomForest_top6_temporal": RandomForestClassifier(n_estimators=120, max_depth=14, random_state=42, n_jobs=-1, class_weight="balanced_subsample")
    }.items():
        pipe = Pipeline([("pre", make_preprocessor(X_train, top6)), ("model", model)])
        pipe.fit(X_train[top6], y_train)
        pred = pipe.predict(X_test[top6])
        temporal_results.append({
            "attack_code": code, "attack": attack, "folder": folder,
            "target_col": target_col, "split": "temporal_first70_last30",
            "rows_used": len(X), "normal_train": int((y_train == 0).sum()),
            "attack_train": int((y_train == 1).sum()),
            "normal_test": int((y_test == 0).sum()),
            "attack_test": int((y_test == 1).sum()),
            "model": name, "num_features": 6, **metrics(y_test, pred)
        })

pd.DataFrame(temporal_results).to_csv(OUT / "actual_dataset_temporal_split_results.csv", index=False)
pd.DataFrame(temporal_selected).to_csv(OUT / "selected_top6_features_temporal_split.csv", index=False)

print("Done. Results saved in:", OUT.resolve())
